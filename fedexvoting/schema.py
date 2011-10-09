from colander import MappingSchema
from colander import SequenceSchema
from colander import SchemaNode
from colander import String
from colander import DateTime
from colander import Float
from colander import Int
from deform import widget


class CategorySchema(MappingSchema):
    vote_category = SchemaNode(String())
    weight = SchemaNode(Float())


class CategoriesSchema(SequenceSchema):
    category = CategorySchema()


class VotingBoothSchema(MappingSchema):
    title = SchemaNode(
        String(),
        description="The title will be displayed on the front page"
        )
    start = SchemaNode(DateTime())
    end = SchemaNode(DateTime())
    categories = CategoriesSchema()


class TeamSchema(MappingSchema):
    title = SchemaNode(String())
    # TODO: Turn this into rich text?
    description = SchemaNode(String(), missing='')


class TeamVoteSchema(MappingSchema):
    # hidden value that has the team id in it
    team_hidden = SchemaNode(
        Int(),
        widget=widget.HiddenWidget(),
    )
    # read-only friendly presentation of the team name
    team_title = SchemaNode(
        String(),
        missing='',
        widget=widget.TextInputWidget(
            template="readonly_textinput",
            css_class="teamTitle",
        ),
    )
    # read-only friendly presentation of the team description
    team_description = SchemaNode(
        String(),
        missing='',
        widget=widget.TextInputWidget(
            template="readonly_textinput",
            css_class="teamDescription",
        ),
    )


class VoteSchema(SequenceSchema):
    vote = TeamVoteSchema()


class BallotSchema(MappingSchema):
    votes = VoteSchema()
