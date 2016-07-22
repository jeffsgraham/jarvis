from django.test import TestCase
from inventory.models import *
import copy

class ItemTestCase(TestCase):
    def setUp(self):
        self.key = 'ipAddress'
        self.value = '10.221.248.123'
        self.type_scaler = Type.objects.get_or_create(name="Video Scaler")[0]
        self.man_extron = Manufacturer.objects.get_or_create(name="Extron")[0]
        self.mod_dvs = Model.objects.get_or_create(name="DVS304")[0]
        Item.objects.create(itemType=self.type_scaler, manufacturer=self.man_extron, \
            model=self.mod_dvs, attributes={'serial':"1234Serial", 'sid':"B078989"})

        self.type_comp = Type.objects.get_or_create(name="Computer")[0]
        self.man_hp = Manufacturer.objects.get_or_create(name="HP")[0]
        self.mod_dc8300 = Model.objects.get_or_create(name="DC8300")[0]
        Item.objects.create(itemType=self.type_comp, manufacturer=self.man_hp, model=self.mod_dc8300, \
                attributes={'serial':"qweqtrt1234", self.key:self.value})

    def test_simple_revision(self):
        #retrieve and alter computer item
        compType = Type.objects.get(name="Computer")
        comp1 = Item.objects.raw_query({'itemType_id':compType.name})[0]
        newValue = '10.221.248.231'
        comp1.attributes[self.key]= newValue
        comp1.save_with_revisions()
        comp2 = Item.objects.raw_query({'itemType_id':compType.name})[0]
        self.assertNotEqual(comp2.attributes[self.key], self.value, \
                "Altered item == to previous state")
        
        #revert
        rev = ItemRevision.objects.get(item=comp2)
        comp2.revert(rev)
        comp3 = Item.objects.raw_query({'itemType_id':compType.name})[0]
        self.assertEqual(comp3.attributes[self.key], self.value, \
                "reverted item != previous state")

        #check that rev has been removed from DB
        revSearch = ItemRevision.objects.filter(id=rev.id)
        self.assertTrue(len(revSearch) == 0, "ItemRevision not deleted from DB")

    def test_delete_revisions(self):
        #delete Item
        computer = Item.objects.raw_query({'itemType_id':self.type_comp.name})[0]
        computer.delete()

        #still exists in DB
        c1 = Item.objects.raw_query({'itemType_id':self.type_comp.name})[0]
        self.assertTrue(c1.id == computer.id)

        #is set to active == false
        self.assertTrue(c1.active == False)

        #check revision
        rev = ItemRevision.objects.get()
        self.assertTrue(rev.changes['active'] == True)

        #revert item
        c1.revert(rev)
        c2 = Item.objects.raw_query({'itemType_id':self.type_comp.name})[0]
        self.assertTrue(c1.active == True)


    def test_complex_revision(self):
        #get items from DB
        computer = Item.objects.raw_query({'itemType_id':self.type_comp.name})[0]
        altered = copy.deepcopy(computer)
        scaler = Item.objects.raw_query({'itemType_id':self.type_scaler.name})[0]
        self.assertTrue(computer == altered)

        #alter item
        altered.item = scaler
        self.assertEqual(altered.item, scaler, "Newly assigned sub-item not equal to itself")
        altered.itemType = Type.objects.get_or_create(name="Switcher")[0]
        altered.model = Model.objects.get_or_create(name="MLS506MA")[0]
        altered.manufacturer = Manufacturer.objects.get_or_create(name="Extron")[0]
        altered.attributes['serial'] = "MXL1234"
        del altered.attributes[self.key]
        altered.save_with_revisions()
        self.assertFalse(computer == altered)

        #check that revision was generated
        revs = ItemRevision.objects.all()
        self.assertTrue(len(revs) == 1) #has one rev object
        

        #revert changes
        altered.revert(revs[0])
        self.assertTrue(altered == computer)

    def test_iterative_revision(self):
        #get items from DB
        computer = Item.objects.raw_query({'itemType_id':self.type_comp.name})[0]
        altered = copy.deepcopy(computer)
        scaler = Item.objects.raw_query({'itemType_id':self.type_scaler.name})[0]
        self.assertTrue(computer == altered)

        #alter item
        count = 0 #init rev counter
        altered.item = scaler
        altered.save_with_revisions()
        count += 1
        
        altered.itemType = Type.objects.get_or_create(name="Switcher")[0]
        altered.save_with_revisions()
        count += 1
        
        altered.model = Model.objects.get_or_create(name="MLS506MA")[0]
        altered.save_with_revisions()
        count += 1
        
        altered.manufacturer = Manufacturer.objects.get_or_create(name="Extron")[0]
        altered.save_with_revisions()
        count += 1
        
        altered.attributes['serial'] = "MXL1234"
        altered.save_with_revisions()
        count += 1
        
        del altered.attributes[self.key]
        altered.save_with_revisions()
        count += 1
        

        #check that revisions were generated
        revs = ItemRevision.objects.filter(item=altered).order_by('revised')
        self.assertTrue(len(revs) == count)
        

        #revert changes
        self.assertFalse(computer == altered)
        altered.revert(revs[0])
        self.assertTrue(altered == computer)
        
        #check that revisions were deleted
        revs = ItemRevision.objects.filter(item=altered).order_by('revised')
        self.assertTrue(len(revs) == 0)
  
    def test_missing_fkey_revisions(self):
        computer = Item.objects.raw_query({'itemType_id':self.type_comp.name})[0]
        scaler = Item.objects.raw_query({'itemType_id':self.type_scaler.name})[0]

        #alter item
        computer.item = scaler
        computer.save_with_revisions()
        
        #alter item back
        computer.item = None #models.SET_NULL
        computer.save_with_revisions()

        #delete previously linked item
        scalerId = scaler.id #store scaler id for later comparison
        #do actual DB deletion (since Item.delete() is overloaded to not lose data
        super(Item, scaler).delete() 
        self.assertTrue(len(Item.objects.raw_query({'itemType_id':self.type_scaler.name, 'active':True})) == 0)

        #revert to old revision
        rev2 = ItemRevision.objects.filter(item=computer).order_by('-revised')[0]
        self.assertTrue(rev2.changes['item'] == scalerId)
        computer.revert(rev2)
        self.assertTrue(computer.item_id == None)
