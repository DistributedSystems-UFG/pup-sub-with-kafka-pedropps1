# Sistema de Chat Pub/Sub com Apache Kafka

Este projeto implementa um sistema de chat em grupo baseado em tópicos utilizando **Apache Kafka** como plataforma de streaming de eventos. A aplicação demonstra os conceitos de Produtores e Consumidores Kafka para construir um sistema de comunicação em tempo real, onde cada canal de chat corresponde a um tópico do Kafka.

## Arquitetura e Conceitos Chave do Kafka

A aplicação é construída sobre a arquitetura cliente-servidor do Kafka:

1.  **Kafka Broker:** É o servidor central que gerencia os tópicos. Diferente de um broker simples como o do ZeroMQ, o Kafka Broker armazena as mensagens de forma persistente em um log distribuído, permitindo durabilidade e re-leitura de mensagens. Para esta tarefa, o broker é executado facilmente via Docker.
2.  **Cliente de Chat (`chat_client.py`):** Cada usuário executa este programa, que atua como:
    *   **Produtor:** Envia mensagens (em formato JSON) para os tópicos do Kafka.
    *   **Consumidor:** Lê mensagens dos tópicos. Para permitir o envio e recebimento simultâneos, o consumidor é executado em uma thread separada.
3.  **Consumer Groups:** Este é um conceito fundamental no Kafka. Para que cada cliente de chat receba sua própria cópia de todas as mensagens de um tópico (comportamento de broadcast/pub-sub), cada instância do cliente é configurada com um **`group_id` único e aleatório**. Se todos os clientes compartilhassem o mesmo `group_id`, o Kafka distribuiria as mensagens entre eles, e cada cliente receberia apenas um subconjunto das mensagens (comportamento de fila de trabalho).

## Pré-requisitos

**1. Docker e Docker Compose**

Kafka é um sistema complexo que requer um serviço de servidor (e seu coordenador, Zookeeper). A maneira mais fácil e recomendada de executar isso localmente é via Docker.
*   [Instale o Docker]
*   [Instale o Docker Compose]

**2. Biblioteca Python**

Você precisará da biblioteca `kafka-python`. Instale-a com pip:
```bash
pip3 install kafka-python
```

## Como Executar o Sistema

**1. Iniciar o Servidor Kafka**

Com o Docker em execução, navegue até a pasta do projeto no terminal e inicie os serviços Kafka e Zookeeper usando o arquivo `docker-compose.yml` fornecido:
```bash
docker-compose up -d
```
Este comando fará o download das imagens necessárias (na primeira vez) e iniciará os servidores em segundo plano. **Aguarde cerca de um minuto** para que o Kafka se inicialize completamente. Você pode verificar se os contêineres estão em execução com `docker ps`.

**2. Iniciar os Clientes de Chat**

Para cada usuário, abra um novo terminal e execute o cliente:
```bash
python3 chat_client.py
```
O programa solicitará:
1.  Seu **nome de usuário** (ex: `Alice`).
2.  O **canal (tópico) inicial** que deseja entrar (ex: `geral`).

**3. Usando o Chat**

O uso é similar a um cliente de IRC:
*   **Para enviar uma mensagem:** Simplesmente digite sua mensagem e pressione Enter. Ela será enviada para o seu canal ativo.
*   **Para usar comandos:**

| Comando         | Descrição                                         |
|-----------------|---------------------------------------------------|
| `/help`         | Mostra a lista de comandos.                       |
| `/join <canal>`   | Entra em um novo canal (assina um novo tópico).   |
| `/switch <canal>` | Muda o seu canal ativo (tópico para onde você envia).|
| `/quit`         | Sai do chat de forma limpa.                       |

*Observação: Nomes de canais não podem conter caracteres especiais como `#`.*

**4. Encerrar o Servidor Kafka**

Quando terminar os testes, você pode parar e remover os serviços do Kafka para liberar recursos com o comando:```bash
docker-compose down
```