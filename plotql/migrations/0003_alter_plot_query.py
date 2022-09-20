# Generated by Django 3.2.14 on 2022-09-20 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plotql', '0002_auto_20220909_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plot',
            name='query',
            field=models.CharField(default='\nquery {\n    GROUP: experiment(id: 42) {\n      OBJECT: id\n      TYPE: __typename\n      NAME: name\n      \n      GROUP_HYPER_AS_BAD_SAMPLES: samples(tags: "bad") {\n        OBJECT: id\n         TYPE: __typename\n        NAME: name\n        GROUPS: representations(variety: VOXEL){\n          NAME: name\n          OBJECT: id\n          TYPE: __typename\n\n\n          FLATDATUM_OBJECT_AS_INDEX: id\n          FLATDATUM_VALUE_AS_INDEX: id\n          FLATDATUM_TYPE_AS_INDEX: __typename\n  \n          DATUM_AS_TIME: omero {\n            VALUE_FROM_DATE: acquisitionDate\n          }\n          \n          DATUM_AS_EXPOSURE_TIME: omero{\n            OBJECT: id\n            TYPE: __typename\n            VALUE_FROM_SUM: planes {\n              VALUE_FROM_FLOAT: exposureTime\n            }\n          }\n          \n          DATUM_FIRST_AS_INCREASING: metrics(keys: "Increasing"){\n            VALUE_FROM_INT: value\n          }\n          \n          DATUM_FIRST_AS_CELL_AREA: labels {\n            OBJECT: id\n            TYPE: __typename\n            VALUE_FROM_SUM: features(keys: "Area"){\n              VALUE_FROM_FLOAT: value\n            }\n          }\n          \n        }\n          \n        }\n        \n      \n\n      GROUP_HYPER_AS_ELEMENTAL_SAMPLES: samples(tags: "elemental") {\n        OBJECT: id\n         TYPE: __typename\n        NAME: name\n        GROUPS: representations(variety: VOXEL){\n          NAME: name\n          OBJECT: id\n          TYPE: __typename\n\n\n          FLATDATUM_OBJECT_AS_INDEX: id\n          FLATDATUM_VALUE_AS_INDEX: id\n          FLATDATUM_TYPE_AS_INDEX: __typename\n  \n      \n          DATUM_AS_EXPOSURE_TIME: omero{\n            OBJECT: id\n            TYPE: __typename\n            VALUE_FROM_SUM: planes {\n              VALUE_FROM_FLOAT: exposureTime\n            }\n          }\n          \n          \n        }\n          \n        }\n  }\n}\n', max_length=10000),
        ),
    ]
