from colander import MappingSchema
from colander import SchemaNode
from colander import String
from colander import DateTime


class VotingBoothSchema(MappingSchema):
    title = SchemaNode(
        String(),
        description="The title will be displayed on the front page"
        )
    start = SchemaNode(DateTime())
    end = SchemaNode(DateTime())
