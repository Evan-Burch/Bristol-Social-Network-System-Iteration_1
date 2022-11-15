from unittest import TestCase
from applayer.collaboration import Collaboration
from applayer.artist import Artist


class TestCollaboration(TestCase):

    def setUp(self):
        self.artist_0 = Artist(1141488, "Tenneva Ramblers", "", "", 0)
        self.artist_1 = Artist(1878533, "Claude Grant", "", "", 0)
        self.roles_0 = ["Vocals [Uncredited], Guitar [Uncredited]",
                        "Written-By",
                        "Written-By",
                        "Arranged By",
                        "Written-By",
                        "Written-By",
                        "Written-By",
                        "Written-By",
                        "Written-By",
                        "Written-By"]
        self.collaboration_0 = Collaboration(self.artist_0, self.artist_1, self.roles_0)

        self.artist_2 = Artist(4610057, "Logan County Trio", "Short Creek Trio", "", 0)
        self.artist_3 = Artist(1862339, "Marion Underwood", "", "", 0)
        self.roles_1 = ["Banjo [Uncredited]"]
        self.collaboration_1 = Collaboration(self.artist_2, self.artist_3, self.roles_1)

    def test_artist0(self):
        self.assertEqual(self.artist_0, self.collaboration_0.artist0)
        self.assertEqual(self.artist_2, self.collaboration_1.artist0)

    def test_artist1(self):
        self.assertEqual(self.artist_1, self.collaboration_0.artist1)
        self.assertEqual(self.artist_3, self.collaboration_1.artist1)

    def test_roles(self):
        self.assertEqual(self.roles_0, self.collaboration_0.roles)
        self.assertEqual(self.roles_1, self.collaboration_1.roles)