from pyramid.threadlocal import get_current_request
from colander import MappingSchema
from colander import SequenceSchema
from colander import SchemaNode
from colander import String
from colander import DateTime
from colander import Float
from colander import Int
from colander import Function
from colander import deferred
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


def one_category(categories):
    return len(categories)


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
    categories = CategoriesSchema(
        validator=Function(
            one_category,
            "You must set up at least one category"),
    )


class MembersSchema(SequenceSchema):
    member = SchemaNode(String())


@deferred
def member_widget(node, kw):
    request = kw['request']
    profiles = request.root['profiles']
    profile_values = list(profiles.values())
    profile_values.sort(key=lambda x: x.last_name)
    vocab = []
    names = set()
    for profile in profile_values:
        fullname = "%s %s" % (profile.first_name, profile.last_name)
        if fullname in names:
            names.add(fullname)
            fullname = '%s (%s)' % (fullname, profile.username)
        else:
            names.add(fullname)
        vocab.append((profile.username, fullname))
    if node.name in ['leader']:
        vocab.insert(0, ('', 'Select a value'))
        return widget.SelectWidget(values=vocab)
    return widget.CheckboxChoiceWidget(values=vocab)


class TeamSchema(MappingSchema):
    title = SchemaNode(String())
    description = SchemaNode(
        String(),
        missing='',
        widget=widget.RichTextWidget(),
    )
    members = MembersSchema(
        widget=member_widget,
        missing=[],
    )
    leader = SchemaNode(
        String(),
        missing='',
        widget=member_widget,
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
        widget=widget.RichTextWidget(
            template="richtext_output",
            css_class="teamDescription",
        ),
    )
    # read-only friendly presentation of the team members
    team_members = SchemaNode(
        String(),
        missing='',
        widget=widget.TextInputWidget(
            template="readonly_textinput",
            # XXX: changeme...
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
