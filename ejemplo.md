# DMND5158443 - Reportes automaticos DATA LAKE

## Metadatos
- numero_demanda: 5158443
- fecha: 10-04-2026
- ciclo: 104
- sistema: COMEX
- version: 1
- autor: Ronald Petrussa

---

## Informacion General

Desarrollo de interfaces automaticas para envio de datos al DATA LAKE de Brasil.

## Historial de Versiones

| Version | Comentario | Numero de llamado | Fecha | Autor |
|---------|-----------|-------------------|-------|-------|
| 1.0 | Primera version | DMND5158443 | 10-04-2026 | Ronald Petrussa |

## Necesidad

Es necesario en este desarrollo generar nuevas interfaces que generen archivos diferentes para luego enviar a Brasil.

## Objetivos y Condiciones

Contar con 3 nuevas interfaces que alimenten las bases de datos de Brasil, para generar KPIs.

## Descripcion de las Actividades

Este nuevo desarrollo generara 3 nuevas interfaces, las cuales generaran 3 archivos txt con informacion de: Despachos, Facturas de Importacion y Exportacion, DDJJ, Estructura, Descargas y Cancelaciones, Saldos, LMAN.

### Flujo de operacion actual

Actualmente este flujo no existe en el sistema COMEX.

### Flujo de operacion - Como deberia funcionar

- Este nuevo desarrollo generara 3 nuevas interfaces
- Las cuales generaran 3 archivos txt con informacion de:
  - Despachos
  - Facturas de Importacion y Exportacion
  - Estructuras

## Reglas para el Desarrollo

### 5.1 DATA LAKE - General

Esta interface debera ejecutar y obtener los siguientes informes:
- Despachos
- Facturas de Importacion y Exportacion
- DDJJ
- Estructura
- Descargas y Cancelaciones
- Saldos
- LMAN

### EndPoint DataLake_ObtenerEstructura

**Nombre:** Get_DataLake_ObtenerEstructura

**1. Objetivo**

El objetivo de este Endpoint es extraer y estructurar informacion de consumos de piezas registrada en el sistema COMEX.

**2. Origen de la informacion**

La informacion se obtiene desde la tabla: MR_DescargaDetalle

Mediante una consulta SQL que selecciona los campos relevantes:

```sql
SELECT
    Documento,
    codigoProducto AS Modelo,
    CASE WHEN P.Origen = '000'
    THEN 'N'
    WHEN P.Origen = '999' OR P.Origen IS NULL
    THEN 'O'
    ELSE 'I' END AS Origen,
    dd.plano as CodigoPieza,
    cantidadDescargada as Uso
FROM Mr_Descarga d
INNER JOIN Mr_DescargaDetalle dd ON d.numero = dd.numero
INNER JOIN Ma_Piezas P ON P.Plano = dd.plano
WHERE d.fechaDescarga >= '01-11-2025'
    AND d.estado IN ('T','S')
    AND documento NOT IN (
        SELECT documento FROM MA_EnvioDocumentacion
    )
```

**3. Descripcion funcional**

Cada registro representa el consumo de una pieza asociada a un modelo, indicando su origen, cantidad utilizada y documento asociado.

**4. Reglas de formateo**

- Campo Uso: formato numerico de 12 enteros y 3 decimales, sin punto ni coma.
- Ejemplo: Valor real: 123,45 -> Valor enviado: 000000123450
- Campos alfanumericos (char): se completan con espacios a la derecha.

**5. Condicion de envio**

Solo se incluyen registros donde el documento no haya sido enviado anteriormente.

**6. Control de Auditoria**

Registraremos cada envio en la tabla MA_EnvioDocumentacion.

```sql
CREATE TABLE [dbo].[MA_EnvioDocumentacion](
    [Proceso] [varchar](50) NOT NULL,
    [SubProceso] [varchar](50) NOT NULL,
    [Documento] [varchar](50) NOT NULL,
    [FechaEnvio] [datetime] NULL,
    CONSTRAINT [PK_MA_EnvioDataLake] PRIMARY KEY CLUSTERED
    (
        [Proceso] ASC,
        [SubProceso] ASC,
        [Documento] ASC
    )
) ON [PRIMARY]
GO
```

### Estructura de Datos - Registro Cabecera

| N do Campo | Campo | Inicio | Fin | Tamano | Formato | Digitos decimales | Observaciones | Ejemplo |
|------------|-------|--------|-----|--------|---------|-------------------|---------------|---------|
| 01 | Cod movimiento | 001 | 004 | 004 | char(4) | | 0000 Por defecto | 0000 |
| 02 | Ente_Emisor | 005 | 008 | 004 | char(4) | | COMEX | COMEX |
| 03 | Ente_Destino | 009 | 016 | 008 | char(8) | | DATALAKE | DATALAKE |
| 04 | Fecha_Emision | 017 | 032 | 016 | char(16) | | AAAAMMDDHHMMSS | 20260410143000 |

## Criterios de Aceptacion

- Poder generar reportes automaticos de COMEX.
- Los archivos deben respetar el layout definido por el area de Brasil.
- El secuencial debe incrementarse correctamente por cada envio.

## Aprobaciones

Las aprobaciones podran enviarse via E-mail, colocando el siguiente texto:

"Se aprueba el Analisis Funcional DMND5158443 para la realizacion del mismo."
