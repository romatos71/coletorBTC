const express = require('express');
const redis = require('redis');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

// Configuração da conexão com o Redis
// (Se estiver rodando no OpenShift, ele vai ler a variável de ambiente REDIS_URL automaticamente)
const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';
const client = redis.createClient({ url: redisUrl });

client.connect().catch(err => console.error('Erro ao conectar no Redis:', err));

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Rota da API que entrega os dados de bitcoin para a tela
app.get('/api/bitcoin', async (req, res) => {
    try {
        // Pega as últimas 1000 entradas do histórico armazenadas no Redis
        const rawData = await client.zRange('bitcoin_history', -1000, -1);
        const history = rawData.map(item => JSON.parse(item));
        
        // Pega o preço mais recente (último elemento do array)
        const latest = history[history.length - 1] || { usd: 0, brl: 0 };

        res.json({ latest, history });
    } catch (e) {
        console.error(e);
        res.status(500).json({ error: 'Erro ao buscar dados do Redis' });
    }
});

app.listen(port, () => {
    console.log(`Servidor rodando na porta ${port}`);
});