# lp-url-redirect

Servicio serverless para redirigir URLs cortas con Python 3.12, AWS Lambda, API Gateway HTTP API, DynamoDB y Terraform.

## Endpoint

`GET /{codigo}`

### Respuesta exitosa

```http
HTTP/1.1 302 Found
Location: <URL_LARGA>
```

### URL inexistente

```json
{
  "error": "URL not found",
  "code": "<CODIGO>"
}
```

## Validar antes de deploy

```powershell
python -m venv .venv
pip install -r requirements.txt
$env:DYNAMODB_TABLE = "urls"
python -m unittest discover tests
```

## Deploy
```bash
terraform init
terraform validate
terraform plan
terraform apply
terraform destroy
```

Antes de aplicar, crea `terraform/terraform.tfvars` tomando como base `terraform/terraform.tfvars.example`.

Puedes obtener el id correcto desde el modulo `lp-url-shortener`:

```powershell
cd D:\lp-url-shortener\terraform
terraform output api_gateway_id
```

```hcl
aws_region          = "<REGION_AWS>"
dynamodb_table_name = "<TABLA_URLS>"
stats_table_name    = "<TABLA_STATS>"
api_gateway_id      = "<API_GATEWAY_ID>"
environment         = "<AMBIENTE>"
```

`api_gateway_id` debe ser solo el id del HTTP API existente, no la URL completa, no el account id y no `yes`.

## Probar en Postman

Importa la collection:

```text
postman/Acortador de URLs.postman_collection.json
```

Variables de la collection:

- `api_base_url`: endpoint del API Gateway, sin slash final.
- `codigo_valido`: codigo existente en DynamoDB para validar el `302`.
- `codigo_inexistente`: codigo que no exista para validar el `404`.

Para ver el `302`, deja desactivado `Follow redirects` en la request `Redirect URL - codigo valido`.

## Recursos creados por Terraform

- Lambda Python 
- IAM role con permisos minimos de logs, `dynamodb:GetItem` y `dynamodb:UpdateItem`.
- Integracion Lambda proxy.
- Ruta `GET /{codigo}` en el API Gateway HTTP API existente.

## Buenas practicas

- El contador de clicks se incrementa con `UpdateItem` y `ADD clicks :inc`.
- El 404 devuelve JSON estructurado con `error` y `code`.
- El 302 devuelve solo el header `Location`.
- El codigo se lee con `.get()` desde `pathParameters` para evitar `KeyError`.
