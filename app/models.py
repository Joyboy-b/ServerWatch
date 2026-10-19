from dataclasses import dataclass

@dataclass
class Server:
    id: str
    cpu: float 
    memory: float 
    online: bool 

