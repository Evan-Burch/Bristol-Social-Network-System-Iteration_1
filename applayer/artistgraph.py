from applayer.graphbase import GraphBase
from applayer.artistlist import ArtistList
from applayer.artist import Artist
from applayer.collaboration import Collaboration
from datalayer.mongobridge import MongoBridge
from typing import List
from datalayer.artistnotfound import ArtistNotFound
from multipledispatch import dispatch


class ArtistGraph(GraphBase):

    @dispatch()
    def __init__(self):
        super().__init__()
        self.__artists: List[Artist] = []
        self.__collaborations: List[Collaboration] = []

    @dispatch(ArtistList, int)
    def __init__(self, artist_list: ArtistList, depth: int) -> None:
        super().__init__()
        self.__artists: List[Artist] = []
        self.__collaborations: List[Collaboration] = []
        self.__mongo: MongoBridge = MongoBridge("mongodb://localhost:27017/", "BristolData", "Artists")

        # Add each artist to artists
        self.__artists = artist_list.artist_objects.copy()
        for i in self.__artists:
            super().add_node(i)

        level: int = 1
        artists_at_depth: int = len(self.__artists)
        artists_added: int = 0
        for i in self.__artists:
            if artists_added == artists_at_depth:
                level += 1
                artists_added = 0
                artists_at_depth = len(self.__artists) - artists_at_depth

            artists_added += 1
            # Check if each collaborator exists in the database as its own Artist. If it does then make an
            # Artist with the data found. If it doesn't then make an Artist from scratch. Add role data to roles
            for j in i.collaborators:
                try:
                    artist_info: dict = self.__mongo.get_artist_by_id(j["collaboratorID"])
                    second_artist: Artist = Artist(artist_info)
                    second_artist.level = level
                except ArtistNotFound:
                    second_artist: Artist = Artist(j["collaboratorID"], j["collaboratorName"], "", "", level)

                # If this artist has not been added to the graph yet, add it
                if not super().has_node(second_artist):
                    if second_artist.level < depth:
                        self.add_artist(second_artist)
                    super().add_node(second_artist)

                roles: List[str] = []
                if j["roles"] is not None:
                    for k in j["roles"]:
                        roles.append(k)

                if not super().has_edge(i, second_artist):
                    # Make new collaboration and add it to collaborations
                    new_collaboration: Collaboration = Collaboration(i, second_artist, roles)
                    self.__collaborations.append(new_collaboration)
                    super().add_edge(i, second_artist)
                else:
                    super().incr_edge(i, second_artist)

    def add_collaboration(self, collab: Collaboration) -> None:
        if not super().has_edge(collab.artist0, collab.artist1):
            super().add_edge(collab.artist0, collab.artist1)
            self.__collaborations.append(collab)
        else:
            super().incr_edge(collab.artist0, collab.artist1)

    def add_artist(self, artist: Artist) -> None:
        if not super().has_node(artist):
            super().add_node(artist)
            self.__artists.append(artist)

    @property
    def artists(self) -> List[Artist]:
        return self.__artists

    @property
    def collaborations(self) -> List[Collaboration]:
        return self.__collaborations
