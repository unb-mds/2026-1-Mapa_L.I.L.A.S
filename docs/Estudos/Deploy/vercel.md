# Deploy de Aplicações na Vercel
Objetivo: Padronizar o processo de publicação (deploy), configuração de variáveis e fluxo de trabalho (CI/CD) utilizando a plataforma Vercel.

1. Pré-requisitos
Antes de iniciar um deploy, certifique-se de que você possui:

- [ ] Acesso ao repositório do projeto no provedor de Git (GitHub/GitLab/Bitbucket).

- [ ] Conta ativa na Vercel com permissão de acesso ao Team (caso seja um projeto em equipe).

- [ ] Lista de Variáveis de Ambiente (.env) necessárias para a aplicação rodar em Produção.

2. Configurando o Projeto pela Primeira Vez
Se o projeto ainda não existe na Vercel, siga este passo a passo:

    1. Acesse o painel da Vercel e clique em "Add New..." > "Project".

    2. Na seção Import Git Repository, localize o repositório do projeto e clique em "Import".

    3. Em Configure Project, preencha os dados:

- Project Name: O nome padrão do repositório ou um nome amigável (ex: meu-projeto-frontend).

- Framework Preset: A Vercel geralmente detecta automaticamente (ex: Next.js, React, Vite). Se não detectar, selecione o correto na lista.

- Root Directory: Altere apenas se o seu projeto não estiver na pasta raiz (ex: monorepos).

    4. Em Environment Variables, adicione todas as chaves e valores presentes no arquivo .env de produção.

    5. Clique em "Deploy".

    6. Aguarde o build. Se ocorrer sucesso, a Vercel gerará os domínios de acesso automaticamente.

3. Fluxo de Trabalho e Ambientes (CI/CD)
O nosso processo de deploy é 100% automatizado via Git. Não é necessário realizar deploys manuais por linha de comando, a menos que haja uma exceção justificada.

Produção (Production)
- Como funciona: Qualquer código que for aprovado e mesclado (merged) na branch main (ou master) será automaticamente publicado no ambiente oficial.

- Gatilho: git push origin main ou aprovação de um Pull Request para a main.

- Domínio: [seu-dominio-oficial.com.br]

Homologação/Testes (Deploy Previews)
- Como funciona: Quando você cria uma nova branch (ex: feature/nova-tela) e envia para o repositório, a Vercel cria uma URL temporária e isolada.

- Objetivo: Testar a funcionalidade na nuvem e enviar o link para o time de QA/Design aprovar antes de ir para a main.

- Onde encontrar o link: O link do Preview ficará disponível automaticamente nos comentários do seu Pull Request (no GitHub/GitLab) ou no painel da Vercel.

4. Gestão de Variáveis de Ambiente
Sempre que uma nova chave for adicionada ao .env local, ela precisa ser adicionada à Vercel.

1. Acesse o projeto na Vercel.

2. Vá em Settings > Environment Variables.

3. Cole o nome da chave e o valor.

4. Selecione os ambientes que terão acesso a essa variável (Production, Preview e/ou Development).

6. Salve.

**Importante:** Alterações nas variáveis de ambiente só entram em vigor no próximo deploy. Após salvar, você precisará ir em "Deployments", clicar nos três pontos do último deploy e selecionar "Redeploy".

5. Como fazer um Rollback (Reverter Deploy)
Se uma atualização quebrar o ambiente de Produção, siga os passos abaixo para voltar à versão anterior imediatamente:

1. Acesse o painel do projeto na Vercel.

2. Clique na aba Deployments.

3. Identifique na lista o último deploy que estava funcionando corretamente (eles são marcados com a data e o commit do Git).

4. Clique nos três pontos (...) ao lado desse deploy e selecione "Promote to Production" ou "Redeploy".

5. O ambiente de Produção voltará a espelhar essa versão antiga.

**Ação Pós-Rollback:** Após o site voltar ao ar, avise a equipe, crie uma branch de correção (hotfix), conserte o erro e abra um novo Pull Request.

## **Dicas de Troubleshooting**
- O Build falhou na Vercel, mas roda na minha máquina: Verifique se você não esqueceu de configurar alguma variável de ambiente na plataforma ou se há diferenças nas versões do Node.js (você pode forçar a versão do Node em Settings > General > Node.js Version).

- Erro de Case Sensitivity: O Windows ignora diferenças entre letras maiúsculas e minúsculas em nomes de arquivos (ex: Botao.js e botao.js), mas os servidores Linux da Vercel não. Certifique-se de que os caminhos de importação no código batem perfeitamente com os nomes dos arquivos.