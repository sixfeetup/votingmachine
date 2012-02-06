from pyramid.threadlocal import get_current_request
from colander import MappingSchema
from colander import SequenceSchema
from colander import SchemaNode
from colander import String
from colander import DateTime
from colander import Float
from colander import Int
from colander import Function
from deform import widget


# Validators
####################################################################

def unique_email(email):
    """XXX: use bind instead of using get_current_request
    """
    root = get_current_request().root
    profiles = root['profiles'].values()
    for profile in profiles:
        if profile.email == email:
            return False
    return True


def unique_username(username):
    root = get_current_request().root
    user_folder = root['users']
    return not username in user_folder.byid


# Schema
####################################################################

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


class MembersSchema(SequenceSchema):
    member = SchemaNode(String())


class TeamSchema(MappingSchema):
    title = SchemaNode(String())
    # TODO: Turn this into rich text?
    description = SchemaNode(String(), missing='')
    members = MembersSchema(widget=widget.CheckboxChoiceWidget())
    leader = SchemaNode(
        String(),
        missing='',
        widget=widget.SelectWidget(),
    )


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


class ProfileSchema(MappingSchema):
    first_name = SchemaNode(String())
    last_name = SchemaNode(String())
    email = SchemaNode(
        String(),
        validator=Function(unique_email, 'Email already in use'),
    )


class ProfileAddSchema(ProfileSchema):
    username = SchemaNode(
        String(),
        validator=Function(unique_username, 'Username already exists'),
    )
    password = SchemaNode(String(), widget=widget.CheckedPasswordWidget())
