# Actividad 5.2 – Compute Sales

Estructura alineada con la carpeta de referencia **A5.2 Archivos de Apoyo**:

- **TC1/**: `TC1.ProductList.json` (catálogo) y `TC1.Sales.json` (ventas).
- **TC2/**: `TC2.Sales.json` (ventas; catálogo = TC1).
- **TC3/**: `TC3.Sales.json` (ventas; catálogo = TC1).
- **Results.txt**: Totales de referencia para comparar.
- **source/**: Programa `computeSales.py` y ejemplos opcionales.

## Uso

```bash
cd source
python computeSales.py ../TC1/TC1.ProductList.json ../TC1/TC1.Sales.json
python computeSales.py ../TC1/TC1.ProductList.json ../TC2/TC2.Sales.json
python computeSales.py ../TC1/TC1.ProductList.json ../TC3/TC3.Sales.json
```

El resultado se muestra en pantalla y se guarda en `source/SalesResults.txt`.
