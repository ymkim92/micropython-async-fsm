```plantuml
@startuml
skinparam state {
    BackgroundColor #FDF6E3
    BorderColor Black
    ArrowColor DarkBlue
    FontSize 14
}

[*] --> Idle : start()

state Idle {
    Idle --> Running : Start [ctx.enabled == True]
    Idle --> Error : Timeout
}

state Running {
    Running --> Idle : Stop
    Running --> Error : Timeout
}

state Error {
}
@enduml
```