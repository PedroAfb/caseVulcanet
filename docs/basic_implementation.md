Implementação Básica:
- A cli deve permitir os comandos call, answer, reject e hangup todos com um argumento de id
- O CallCenter tem operadores que possuem id e estado (disponivel, sendo chamado, ocupado)

Função call:
- Printar na tela
- entregar a chamada para um operador disponivel e setar o estado para sendo chamado
  - Se não tiver nenhum operador disponivel, a chamada deve entrar na fila de espera
  - No momento que algum operador ficar disponível, segue para o próximo passo
- Deixar a chamada na fila de espera do atendente (se o operador está no estado sendo chamado, então ele só pode aceitar ou rejeitar a chamada)

Função answer:
- Printar na tela
- Setar o estado do operador para busy

Função reject:
- Printar na tela
- Setar o estado do operador para avaliable
- A chamada volta para o fim da fila?


Função hangup:
- Se a ligação foi aceita:
    - seta o estado para o operador como disponivel
    - printa na tela
- Se a ligação foi recusada:
    - printa na tela
