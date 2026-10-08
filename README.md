# three-blender

Converte uma cena simples — caixas, esferas, cilindros e cones — num site que dá para girar no navegador.

Não lê `.blend` direto. O Blender continua sendo o modelador: exporte os dados que importam para `scene.json` (ou escreva a cena na mão) e este pacote gera o site. É Python na biblioteca padrão, mais um `viewer.js` que usa Three.js por CDN.

## Rodar

```bash
python -m unittest discover -s tests -t .
python -m three_blender.cli examples/studio.json -o site
python -m http.server -d site
```

Abra o endereço que o servidor mostrar. Arrastar gira. Scroll aproxima.

## Formato

```json
{
  "name": "Estúdio",
  "camera": { "position": [4, 2, 5], "target": [0, 0.6, 0] },
  "objects": [
    { "type": "box", "name": "base", "position": [0, 0.2, 0], "scale": [2, 0.4, 1], "color": "#2c2924" }
  ]
}
```

Tipos: `box`, `sphere`, `cylinder`, `cone`.
