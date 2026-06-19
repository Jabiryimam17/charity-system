USER_REGISTRAR_ABI = {
    "ScoreUpdate":{
        "type":"event",
        "name":"ScoreUpdate",
        "inputs":[
            {"name":"user","type":"address","indexed":True},
            {"name":"role","type":"uint8","indexed":False},
            {"name":"score_type","type":"uint8","indexed":False},
            {"name":"score_delta","type":"int32","indexed":False}

        ]
    }
}