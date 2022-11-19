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

        # Copy level 0 artists to self.__artists and add them to the graph
        self.__artists = artist_list.artist_objects.copy()
        for i in self.__artists:
            super().add_node(i)

        # Variables to keep track of when all artists at current level have been added
        level: int = 1
        artists_at_depth: int = len(self.__artists)
        artists_added: int = 0
        for i in self.__artists:
            # Check if all artists at the current level have been added. If so, increment level
            if artists_added == artists_at_depth:
                level += 1
                artists_added = 0
                artists_at_depth = len(self.__artists) - artists_at_depth
            artists_added += 1

            for j in i.collaborators:
                # If collaborator exists in the database as its own Artist then create an Artist with the data.
                try:
                    artist_info: dict = self.__mongo.get_artist_by_id(j["collaboratorID"])
                    second_artist: Artist = Artist(artist_info)
                    second_artist.level = level
                except ArtistNotFound:
                    # If it doesn't then make an Artist from scratch.
                    second_artist: Artist = Artist(j["collaboratorID"], j["collaboratorName"], "", "", level)

                # If this artist has not been added to the graph yet, add it
                if not super().has_node(second_artist):
                    # Only add artist to list if this artist's collaborators need to be added
                    if second_artist.level < depth:
                        self.add_artist(second_artist)
                    super().add_node(second_artist)

                # Prepare list of roles to be added to the new collaboration
                roles: List[str] = []
                if j["roles"] is not None:
                    for k in j["roles"]:
                        roles.append(k)

                # Make new collaboration and add it to collaborations
                new_collaboration: Collaboration = Collaboration(i, second_artist, roles)
                self.add_collaboration(new_collaboration)

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
