# ATLAS DIGITAL / PROJETO TAMAR

**Do Cerrado ao mar: a experiência dos estudantes do IFB entre ciência, conservação e cultura oceânica.**

Aplicação educativa em Python/Streamlit dedicada ao Projeto TAMAR e preparada para receber os registros reais da equipe.

O atlas contém as 13 seções solicitadas, busca, navegação responsiva, referências institucionais, glossário, download em Markdown, registro de biodiversidade, caderno de memórias e uma galeria preparada para receber o acervo real da equipe.

## Executar no Windows

Abra o PowerShell nesta pasta e rode:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

O terminal exibirá um endereço local, normalmente `http://localhost:8501`.

## Onde editar

- `atlas_content.py`: textos, glossário, referências e metadados das seções.
- `app.py`: visual, navegação e recursos interativos.
- `assets/`: imagens conceituais do atlas.
- `assets/galeria/`: fotografias autorizadas da equipe. O nome do arquivo vira a legenda inicial.

Exemplo: `atividade_tamar_turma.jpg` aparece como “Atividade Tamar Turma”. Para legendas mais completas, ajuste o código em `render_gallery()`.

## Cuidados editoriais

- Não apresente as imagens conceituais geradas por IA como registros da visita.
- Inclua espécies apenas quando a identificação estiver apoiada em fotografia, placa, mediação ou outra evidência.
- Confirme autorização antes de publicar nomes, rostos ou informações pessoais de estudantes.
- Atualize a data de consulta quando revisar dados institucionais.

As informações sobre o Centro TAMAR/ICMBio, a Fundação Projeto Tamar e cultura oceânica foram verificadas em fontes institucionais e públicas. A biblioteca completa aparece na seção 13. Consulta editorial: 6 de outubro de 2026.

