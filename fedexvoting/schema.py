from colander import MappingSchema
from colander import SequenceSchema
from colander import SchemaNode
from colander import String
from colander import DateTime
from colander import Float


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
