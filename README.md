# WhatsApp Media Decrypt

Script em **Python** para **descriptografar arquivos de mídia do WhatsApp (.enc)** utilizando a `media_key` armazenada no banco de dados `msgstore.db`.

Este script foi desenvolvido para **fins de computação forense**, permitindo recuperar mídias a partir das URLs presentes na tabela `message_media`.

---

# Exemplo de uso

```
python decrypt_media.py media.enc image 563d2a84e4af8b68a298d900b8bc7e0b273bc2f4e3a9ac11774e4e6a63623495 output.jpg
```

Saída esperada:

```
:: DECRYPT WHATSAPP MEDIA

Input: media.enc
Type: image
Key: 563d2a84e4af8b68...
Output: output.jpg

IV: ...
cipherKey: ...
macKey: ...

Decryption successful.
```

---

# Contexto Forense

Durante a análise do banco de dados do WhatsApp (`msgstore.db`), a tabela:

```
message_media
```

contém informações relevantes sobre arquivos de mídia, incluindo:

- `media_url`
- `media_key`

Mesmo após a visualização de mídias (incluindo **visualização única**), esses registros podem permanecer armazenados no banco.

A `media_url` permite baixar o arquivo criptografado:

```
.enc
```

Para recuperar o conteúdo original, é necessário:

1. Baixar o arquivo `.enc`
2. Extrair a `media_key`
3. Derivar as chaves de criptografia
4. Descriptografar o arquivo usando **AES-CBC**

Este script automatiza esse processo.

---

# Como o WhatsApp protege mídias

O WhatsApp usa o seguinte processo:

1. Cada mídia possui uma **media_key (32 bytes)**.
2. Essa chave é derivada via **HKDF-SHA256**.
3. O resultado gera:

```
IV (16 bytes)
Cipher Key (32 bytes)
MAC Key (32 bytes)
Ref Key (32 bytes)
```

O arquivo `.enc` possui a estrutura:

```
ciphertext || mac
```

Onde:

- `mac` possui **10 bytes**
- o restante é o **ciphertext AES-CBC**

---

# Requisitos

Python 3.8+

Bibliotecas:

```
cryptography
```

Instalação:

```bash
pip install cryptography
```

---

# Uso

```
python decrypt_media.py [input_file] [file_type] [media_key] [output_file]
```

## Argumentos

| Argumento | Descrição |
|---|---|
| `input_file` | arquivo `.enc` baixado da `media_url` |
| `file_type` | tipo da mídia |
| `media_key` | chave hexadecimal presente no `msgstore.db` |
| `output_file` | nome do arquivo de saída |

---

# Tipos de mídia suportados

```
image
video
audio
document
```

Esses valores definem o parâmetro `info` do HKDF usado pelo WhatsApp.

---

# Fluxo do Script

O script executa as seguintes etapas:

### 1️⃣ Parse de argumentos

Utiliza `argparse` para receber os parâmetros da linha de comando.

---

### 2️⃣ Derivação de chaves

A `media_key` é expandida com:

```
HKDF-SHA256
```

gerando:

```
iv
cipher_key
mac_key
ref_key
```

---

### 3️⃣ Leitura do arquivo `.enc`

O script remove o MAC:

```
ciphertext = enc_file[:-10]
```

---

### 4️⃣ Descriptografia

Algoritmo utilizado:

```
AES-256-CBC
```

---

### 5️⃣ Remoção do padding

O WhatsApp utiliza:

```
PKCS7
```

---

### 6️⃣ Escrita do arquivo recuperado

O conteúdo é salvo no arquivo especificado pelo usuário.

---

# Aplicações em perícia digital

Este script pode ser utilizado em:

- análise forense de dispositivos móveis
- investigação de conteúdo de mensagens
- recuperação de mídia apagada
- análise de mensagens de visualização única
- reconstrução de evidências digitais

Ferramentas forenses frequentemente utilizam o mesmo processo internamente, como:

- Cellebrite
- Oxygen
- Magnet AXIOM
- Avilla Forensics

---

# Limitações

- Não realiza verificação do MAC.
- Requer a `media_key` válida.
- O arquivo `.enc` deve estar completo.

---

# Aviso Legal

Este projeto destina-se **exclusivamente para fins educacionais e de investigação forense legítima**.

O uso indevido para acessar dados de terceiros sem autorização pode violar leis de privacidade e crimes informáticos.

Utilize apenas em:

- investigações autorizadas
- perícia judicial
- pesquisa acadêmica

---

# Referências

- WhatsApp Media Encryption
- Signal Protocol
- HKDF RFC 5869
- AES CBC Mode
- WhatsApp Reverse Engineering Research
