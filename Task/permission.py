# permission.py


PERMISSIONS = {

    "Organization": {
        "create": ["owner"],
        "view": ["owner","admin","member"],
        "list":["owner"],
        "update": ["owner"],
        "delete": ["owner"],
    },


    "Team": {
        "create": ["owner","admin"],
        "view": ["owner","admin","member"],
        "update": ["owner","admin"],
        "delete": ["owner","admin"],
    },

    "TeamMembership":{
         "create":["owner","admin"],
         "view": ["owner","admin",],
         "delete": ["owner","admin"],
    },


    "Project": {
        "create": ["owner","admin"],
        "view": ["owner","admin","member"],
        "update": ["owner","admin"],
        "delete": ["owner","admin"],
    },


    "Member": {
        "view": ["owner","admin","member"],
        "add": ["owner","admin"],
        "change_role": ["owner"],
        "remove": ["owner","admin"],
    },

    "Task":{

      "view":["owner","admin","member"],
      "add": ["owner","admin"],
      "update": ["owner","admin"],
      "delete": ["owner","admin"],

    },
    "Comment": {
    "view": ["owner", "admin", "member"],
    "create": ["owner", "admin", "member"],
    "update": ["owner", "admin", "member"],
    "delete": ["owner", "admin", "member"],
},
}