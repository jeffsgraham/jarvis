from datetime import datetime
from djongo import models
#this is used for linking item revisions to the users who initiated them
from django.conf import settings
from inventory.fields import DictFormField


class DictModelField(models.DictField):
    """Provides formfield functionality for DictField
    """
    def formfield(self, **kwargs):
        return models.Field.formfield(self, DictFormField, **kwargs)


class Building(models.Model):
    """stores relevant information about buildings.

    Attributes:
        name (CharField): Building's name.
        abbrev (CharField): Buiding's name abbreviated to three letters.

    """
    _id = models.ObjectIdField()
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=3, unique=True)
    
    def __str__(self):
        return self.name + " (" + self.abbrev + ")"

class Room(models.Model):
    """Stores relevant information about rooms.

    Attributes:
        number (CharField): The room's number , i.e. "101", "304A"...
        building (ForeignKey): The building this room is in.

    """
    _id = models.ObjectIdField()
    number = models.CharField(max_length=10)
    building = models.ForeignKey('Building', on_delete=models.PROTECT, to_field='abbrev')
    schedule_url = models.CharField(max_length=512, blank=True, null=True)


    def __str__(self):
        return self.building.abbrev + " " + self.number
    
    class Meta:
        ordering = ['building','number']

class Manufacturer(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=50, unique=True)

    def cascade_name_change(self, old):
        Item.objects.raw_update({'manufacturer_id':old.name},{'$set':{'manufacturer_id':self.name}})
        Model.objects.raw_update({"manufacturer_id":old.name},{'$set':{"manufacturer_id":self.name}})

    def __str__(self):
        return self.name


class Type(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=50, unique=True)

    def cascade_name_change(self, old):
        Item.objects.raw_update({'itemType_id':old.name},{'$set':{'itemType_id':self.name}})
        Model.objects.raw_update({"itemType_id":old.name},{'$set':{"itemType_id":self.name}})

        
    def __str__(self):
        return self.name

class Attribute(models.Model):
    """Stores Attribute Key suggestions for items.
    
    """
    _id = models.ObjectIdField()
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Model(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=50, unique=True)
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.DO_NOTHING, blank=True, null=True, to_field='name')
    itemType = models.ForeignKey('Type', on_delete=models.DO_NOTHING, blank=True, null=True, to_field='name')
    partNumbers = models.ListField(default=[], blank=True)

    #override objects manager with djongo manager
    #allows raw queries to mongodb
    objects = models.DjongoManager()

    def cascade_name_change(self, old):
        Item.objects.raw_update({'model_id':old.name},{'$set':{'model_id':self.name}})

    def __str__(self):
        return self.name


class Item(models.Model):
    """Stores all information about a single item.

    Attributes:
        itemType (CharField): The type of the described item, i.e. "Computer".
        manufacturer (CharField): The manufacturer of this item.
        model (CharField): The model of equipment this item describes.
        created (DateTimeField): When this item was added to inventory.
        room (ForeignKey): The room (if any) this item resides in.
        item (ForeignKey): The parent item this item is attached to. 
            In the case of a video card this would point to the parent computer.
        active (BooleanField): Whether this item is an active record or 
            historical data.
        attributes (DictField): Item attributes i.e. {Serial: 1234, IP: 1.2.3.4}

    """
    
    #Static Fields
    _id = models.ObjectIdField()
    itemType = models.ForeignKey('Type', on_delete=models.PROTECT, to_field='name')
    manufacturer = models.ForeignKey('Manufacturer', on_delete=models.PROTECT, to_field='name')
    model = models.ForeignKey('Model', on_delete=models.PROTECT, to_field='name')
    created = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey('Room', null=True, blank=True, on_delete=models.SET_NULL)
    item = models.ForeignKey('self', null=True, blank=True, related_name="subItem", on_delete=models.SET_NULL)
    active = models.BooleanField(default=True)

    #Dynamic Fields
    attributes = DictModelField(default={}, blank=True)
    
    #get only active subitems
    def activeSubItems(self):
        return self.subItem.filter(active=True)
    
    @classmethod
    def guessFromSerial2(cls, serial_string):
        """ take 2"""
        cursor = Item.objects.mongo_find({
            "attributes.Serial": {"$regex": "^{0}.+".format(serial_string[0])},
            "$where": "this.attributes.Serial.length == " + str(len(serial_string)),
        })

        def getConfidence(one, two):
            """returns ratio of sequential matching characters between two strings"""
            length = len(one)
            assert length > 0
            assert length == len(two)
            assert one[0] == two[0]
            
            count = 1
            for i in range(1, length):
                if one[i] == two[i]:
                    count += 1
                else:
                    break
            return count/length
        
        matches = {}
        for item in cursor:
            model = item['model_id']
            confidence = getConfidence(serial_string, item['attributes']['Serial'])
            if not model in matches or matches[model]['confidence'] < confidence:
                matches[model] = {
                    'confidence': confidence,
                    'manufacturer': item['manufacturer_id'],
                    'itemType': item['itemType_id'],
                    'model': model
                }
        # return sorted results
        return [v for k, v in sorted(matches.items(), key=lambda x: x[1]['confidence'], reverse=True)]


    @classmethod
    def guessFromSerial(cls, serial_string, room=None):
        """
        Makes an educated guess at what type, model, manufacturer a given
         serial number should be based on existing item entries.

        Returns a new Item instance with suggested values, or None if a guess
         is impossible to make
        """
        #make query for all items staring with the first 2 characters of 
        # serial_string and matching the length of serial_string
        regex_string = '^{0}.{{{1}}}$'.format(serial_string[:2], len(serial_string)-2)
        matches = cls.objects.mongo_find({'attributes.Serial':{'$regex':regex_string}})

        # find most common model
        models = [match['model_id'] for match in matches]
        if models:
            most_common = max(set(models), key=models.count)

            # use most common model's manufacturer and itemType relationship to create an Item instance
            model = Model.objects.filter(name=most_common).first()
            if model:
                print(model)
                print(model.manufacturer)
                print(model.manufacturer_id)
                return cls(
                    model=model,
                    manufacturer=model.manufacturer,
                    itemType=model.itemType,
                    room=room,
                    attributes={'Serial': serial_string}
                )
        # if no similar items are found, return None
        return None

    #override objects manager with djongo manager
    #allows raw queries to mongodb
    objects = models.DjongoManager()

    #Computed Fields
    @property
    def age(self):
        """Compute approximate age in months and years

        Returns:
            Computed age of item as string

        """
        months = ((datetime.now() - self.created).days) / 30
        years = int(months / 12)
        months = int(months % 12)
        #don't clutter output with 0 years
        if years > 0:
            return str(years) + "yrs, " + str(months) + "mo"
        elif months > 1:
            return str(months) + "months"
        elif months == 1:
            return "1month"
        else:
            return "new"

    @classmethod
    def from_pymongo(cls, _id=None, score=None, *args, **kwargs):
        """creates Item instance from pymongo raw query result"""
        return cls(*args, **kwargs)

    @classmethod
    def search(cls, search_term, sort_order=[]):
        """
        search_term (string): the string to search for
        sort_order (list(set(field_name, direction))): A list of sets denoting the requested sorting fields and directions for results

        returns a list of Items matching the search term
        """

        #check that sort order fields are valid
        item_fields = {
            field.name:field.many_to_one 
            for field in cls._meta.fields
        }
        def convert_rel(pair):
            """Helper function for converting relational field names by appending '_id'"""
            return (pair[0] + '_id', pair[1]) if item_fields[pair[0]] else pair
        
        ## filters out any fields that don't exist in the Item class and appends '_id' to relational fields
        sort_list = [convert_rel(pair) for pair in sort_order if pair[0] in item_fields]
        
        # last sort field is how well item matched the search term
        sort_list.append(('score', {'$meta': 'textScore'}))

        # build the search term for pymongo
        querydict = {
            '$text': {
                '$search': search_term
            }
        }
        # do the search and return the result
        results = [
            Item.from_pymongo(**item_dict)
            for item_dict in Item.objects.mongo_find(
                querydict, 
                {'score': {'$meta': 'textScore'}}
            ).sort(sort_list)
        ]

        return results

    def save_without_revisions(self, *args, **kwargs):
        """Expose standard save() method for use"""
        super(Item, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Override default save() method in order to save item revision as well"""
        self.save_with_revisions(*args, **kwargs)

    def save_with_revisions(self, user=None, *args, **kwargs):
        """Add changes to item to rev history and then save the changes
        
        Args:
            user: the user who initiated these changes

        """

        # if no user has been passed as "to blame" 
        # check model instance for a "blame" user
        if not user:
            try:
                user = self.blame
            except AttributeError:
                pass
        
        #get old version of document
        old = Item.objects.filter(pk=self.pk)
        
        #make sure there is an old copy
        if not len(old) == 0:
            old = old[0] #get Item instance from list
  
            #check for any changes
            if(old != self or old.attributes != self.attributes or \
                    old.item != self.item or old.room != self.room):

                #create ItemRevision object
                revision = ItemRevision.objects.create(item=self, user=user)
                
                #store old itemType
                if(old.itemType != self.itemType):
                    revision.changes['itemType'] = old.itemType.name

                #store old manufacturer
                if(old.manufacturer != self.manufacturer):
                    revision.changes['manufacturer'] = old.manufacturer.name

                #store old model
                if(old.model != self.model):
                    revision.changes['model'] = old.model.name

                #store old attributes that have been removed or changed
                for key, value in old.attributes.items():
                    if not (key in self.attributes and self.attributes[key] == value):
                        revision.changes[key] = value

                #store newly aquired attributes as null
                for key, value in self.attributes.items():
                    if not key in old.attributes:
                        revision.changes[key] = None

                #store room
                if(old.room != self.room):
                    if(old.room is not None):
                        revision.changes['room'] = old.room.pk
                    else:
                        revision.changes['room'] = None

                #store item attachment
                if(old.item != self.item):
                    if(old.item is not None):
                        revision.changes['item'] = old.item.pk
                    else:
                        revision.changes['item'] = None
                
                #store active bool
                if(old.active != self.active):
                    revision.changes['active'] = old.active
                
                #save new revision object to DB
                revision.save()

        #save Item instance
        self.save_without_revisions(*args, **kwargs)


    def revert(self, revision):
        """Revert item to state described in specified ItemRevision.

        Args:
            revision: The ItemRevision to be reverted back to.

        """
        #get revision history sorted by date
        revisions = ItemRevision.objects.filter(item=self).order_by("-revised")
        #TODO: check that revision is in revisions list
        for rev in revisions:

            #revert to this revision
            for key, value in rev.changes.items():
                #handle static fields
                if key == 'itemType':
                    self.itemType = Type.objects.get_or_create(name=value)[0]
                elif key == 'manufacturer':
                    self.manufacturer = Manufacturer.objects.get_or_create(name=value)[0]
                elif key == 'model':
                    self.model = Model.objects.get_or_create(name=value)[0]
                elif key == 'room':
                    if(value is not None):
                        try:
                            self.room = Room.objects.get(pk=value)
                        except Room.DoesNotExist:
                            self.room = None
                    else:
                        #set room to None
                        self.room = value
                elif key == 'item':
                    if(value is not None):
                        #catch case where item no longer exists
                        try:
                            self.item = Item.objects.get(pk=value)
                        except Item.DoesNotExist:
                            self.item = None
                    else:
                        #revert to unattached state
                        self.item = value
                elif key == 'active':
                    self.active = value
                elif value is None: #remove new attributes
                    del self.attributes[key]
                else: #revert old attributes
                    self.attributes[key] = value

            #delete revision from DB after reverting
            rev.delete()

            #stop reverting to revisions if this is the last one
            if rev == revision:
                break
        #save reverted state
        self.save_without_revisions()

    def delete(self):
        """Override delete to prevent data loss."""
        self.active = False
        self.save_with_revisions()

    def __eq__(self, compare):
        """Override __eq__() to only compare important fields"""
        #check that object type is the same
        if not isinstance(compare, Item):
            return False
        #check all pertenint variables
        if compare.itemType == self.itemType and \
            compare.manufacturer == self.manufacturer and \
            compare.model == self.model and \
            compare.attributes == self.attributes and \
            compare.item == self.item and compare.room == self.room and \
            compare.active == self.active:
            return True
        else:
            return False

    def __str__(self):
        return str(self.manufacturer) + " " + str(self.itemType)

    class MongoMeta:
        indexes = [
            {'fields': [('$**', 'text')]},
        ]

class ItemRevision(models.Model):
    """Each instance represents changes to a single item at a given time.

    Attributes:
        item (ForeignKey): The item this revision is linked to.
        revised (DateTimeField): The date and time this revision occurred.
        user (ForeignKey): The user who instigated this revision.
        changes (DictField): The changes described by this revision.

    """
    _id = models.ObjectIdField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    revised = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)
    changes = models.DictField(default={})

    def action_taken(self):
        """Returns a list of the actions (changes) that were performed in this revision

        Used primarily for displaying details of this revision to users.
        """
        actions = []
        
        for key, value in self.changes.items():
            #handle static fields
            if key == 'itemType':
                actions.append("Changed Type from " + value)
            elif key == 'manufacturer':
                actions.append("Changed Manufacturer from " + value)
            elif key == 'model':
                actions.append("Changed Model from " + value)
            elif key == 'room':
                room = Room.objects.filter(pk=value).first()
                if not room:
                    room = "Warehouse"
                actions.append("Moved Item from "+ str(room))
            elif key == 'item':
                if value is not None:
                    item = Item.objects.filter(pk=value).first()
                    actions.append("Detached Item from "+ str(item))
                else:
                    actions.append("Attached Item")
            elif key == 'active':
                if value == 'active': #Fixme this is a boolean value, not a string. should be if not value: ...
                    actions.append("Restored Item")
                else:
                    actions.append("Deleted Item")
            elif value is None:
                actions.append("Added Attribute " + key)
            elif key in self.item.attributes:
                actions.append("Changed Attribute from " + key + ": " + value)
            else:
                actions.append("Removed Attribute " + key + ": " + value)
        return actions


    def __eq__(self, compare):
        """Override __eq__() to only compare important fields"""
        if not isinstance(compare, ItemRevision):
            return False
        if self.revised == compare.revised and self.user == compare.user and \
            self.item.pk == compare.item.pk and self.changes == compare.changes:
            return True
        else:
            return False

    def __str__(self):
        return "Item: [" + str(self.item) + "], Revised: [" + str(self.revised) + \
        "], by: [" + str(self.user) + "]"

