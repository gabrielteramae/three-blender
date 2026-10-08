# three-blender — cena JSON vira um site que gira

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-CDN-000000?logo=threedotjs&logoColor=white)

Converte uma cena simples — caixas, esferas, cilindros e cones — num site que dá para girar no navegador. Python na biblioteca padrão gera o HTML; o `viewer.js` desenha com Three.js carregado por CDN.

## Por que não lê `.blend`?

| Dado | Onde fica | Motivo |
|---|---|---|
| Cena (primitivas, cor, câmera) | `scene.json` | Estrutura fixa e fácil de validar. O Blender continua sendo o modelador: o que importa é exportado (ou escrito na mão) nesse JSON. |
| Site (HTML + viewer) | pasta de saída | Gerado aqui. Arrastar gira, scroll aproxima. Sem build, sem `npm install`. |

Tipo desconhecido (`torus`, malha, material) é rejeitado na validação. Não é um importador de Blender.

## Stack

- **Python 3.11+**, zero dependências
- **Three.js por CDN**, só no viewer gerado
- **`unittest`** da biblioteca padrão
- CLI `three-blender` (entrypoint no `pyproject.toml`) ou `python -m three_blender.cli`

## Estrutura

```
three_blender/
├── __init__.py     # export_site, load_scene
├── __main__.py
├── cli.py          # scene.json -o pasta
└── export.py       # valida, grava index.html, scene.json e viewer.js
examples/
└── studio.json     # cena de exemplo (base, poste, lâmpada, marca)
tests/
└── test_export.py
```

## Como rodar

```bash
git clone https://github.com/gabrielteramae/three-blender.git
cd three-blender
python -m unittest discover -s tests -t .
python -m three_blender.cli examples/studio.json -o site
python -m http.server -d site
```

Abra o endereço que o servidor mostrar. `-o` muda a pasta de saída (padrão: `site`).

### Formato

```json
{
  "name": "Estúdio",
  "camera": { "position": [4.2, 2.4, 5.4], "target": [0, 0.6, 0] },
  "objects": [
    { "type": "box", "name": "base", "position": [0, 0.22, 0], "scale": [2.4, 0.44, 1.4], "color": "#2c2924" }
  ]
}
```

Tipos aceitos: `box`, `sphere`, `cylinder`, `cone`.

## Testes realizados

`tests/test_export.py` carrega `examples/studio.json` (4 objetos, incluindo `lampada`), rejeita tipo `torus` com `ValueError`, e confere que a pasta gerada tem `index.html` (com o nome da cena e o `viewer.js`), `scene.json` e `viewer.js`.

---

© 2026 Gabriel Teramae Chan
