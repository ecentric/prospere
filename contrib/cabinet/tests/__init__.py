from document import *
from section import *
from admin_and_command import *
from .. import vote_document
from decimal import Decimal

class CreateNewUser(DocumentTestCase): 
    def test_creation_storage(self):
        user = User.objects.create_user('new_user','new_user@email.ru','password')
        storage = Storages.objects.get(user = user)
        self.assertEqual([storage.mem_limit,storage.title,storage.is_store],[209715200, '', False])

class DocumentVote(DocumentTestCase):

    def test_vote(self):
    	self.assertEqual(self.disseminator_document.count_vote, 0)
    	self.assertEqual(self.disseminator_document.mark, 0)
    	
        vote_document(self.disseminator_document, str(4.5))
        document = Documents.objects.get(id=self.disseminator_document.id)
        self.assertEqual(document.count_vote, 1)
        self.assertEqual(document.mark, Decimal(str(4.5)))

        vote_document(self.disseminator_document.id, 3)
        document = Documents.objects.get(id=self.disseminator_document.id)        
        self.assertEqual(document.count_vote, 2)
        self.assertEqual(document.mark, Decimal(str(3.8)))

