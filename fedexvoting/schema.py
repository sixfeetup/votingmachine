from colander import MappingSchema
from colander import SchemaNode
from colander import String
from colander import Date


class VotingBoothSchema(MappingSchema):
    title = SchemaNode(
        String(),
        description="The title will be displayed on the front page"
        )
    start = SchemaNode(Date())
    end = SchemaNode(Date())
