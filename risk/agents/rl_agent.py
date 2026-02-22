import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional, List
from collections import deque
import random


class RLAgent:
    """Agente de aprendizado por reforço para otimização de portfolio.
    
    Implementa DQN (Deep Q-Network) simplificado para aprender
    políticas de alocação ótimas baseado em estado do mercado.
    """
    
    def __init__(self, state_size: int,
                 action_size: int,
                 learning_rate: float = 0.001,
                 gamma: float = 0.99,
                 epsilon: float = 1.0,
                 epsilon_min: float = 0.01,
                 epsilon_decay: float = 0.995,
                 memory_size: int = 2000):
        """Inicializa agente RL.
        
        Args:
            state_size: Tamanho do vetor de estado
            action_size: Número de ações possíveis
            learning_rate: Taxa de aprendizado
            gamma: Fator de desconto
            epsilon: Taxa de exploração inicial
            epsilon_min: Taxa mínima de exploração
            epsilon_decay: Decaimento de epsilon
            memory_size: Tamanho do replay buffer
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Replay buffer
        self.memory = deque(maxlen=memory_size)
        
        # Q-table simplificado (usar DNN em produção)
        self.q_table = np.zeros((state_size, action_size))
        
        # Estatísticas de treinamento
        self.training_episodes = 0
        self.total_reward = 0.0
        self.episode_rewards = []
    
    def remember(self, state: np.ndarray, action: int,
                reward: float, next_state: np.ndarray,
                done: bool) -> None:
        """Armazena experiência no replay buffer.
        
        Args:
            state: Estado anterior
            action: Ação tomada
            reward: Recompensa recebida
            next_state: Estado seguinte
            done: Se epísodio terminou
        """
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state: np.ndarray, training: bool = True) -> int:
        """Seleciona ação baseado em «epsilon-greedy».
        
        Args:
            state: Estado atual
            training: Se em modo de treinamento
            
        Returns:
            Índice da ação
        """
        # Exploração
        if training and random.random() < self.epsilon:
            return random.randrange(self.action_size)
        
        # Explotação
        state_idx = self._discretize_state(state)
        return np.argmax(self.q_table[state_idx])
    
    def _discretize_state(self, state: np.ndarray) -> int:
        """Discretiza estado contínuo para índice de tabela.
        
        Args:
            state: Vetor de estado
            
        Returns:
            Índice discretizado
        """
        # Normalizando e mapeando para range válido
        normalized = np.clip(state, -1, 1)
        idx = int((normalized[0] + 1) * (self.state_size / 2))
        return np.clip(idx, 0, self.state_size - 1)
    
    def replay(self, batch_size: int) -> None:
        """Treina agente com minibatch do replay buffer.
        
        Args:
            batch_size: Tamanho do minibatch
        """
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            state_idx = self._discretize_state(state)
            next_state_idx = self._discretize_state(next_state)
            
            # Q-learning update
            target = reward
            if not done:
                target = reward + self.gamma * np.max(self.q_table[next_state_idx])
            
            # Atualizar Q-value
            old_value = self.q_table[state_idx, action]
            new_value = old_value + self.learning_rate * (target - old_value)
            self.q_table[state_idx, action] = new_value
        
        # Decair epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def learn_episode(self, env, max_steps: int = 1000,
                     batch_size: int = 32) -> float:
        """Executa um epísodio de treinamento.
        
        Args:
            env: Ambiente (PortfolioEnvironment)
            max_steps: Número máximo de passos
            batch_size: Tamanho do minibatch
            
        Returns:
            Recompensa total do epísodio
        """
        state = env.reset()
        episode_reward = 0.0
        
        for step in range(max_steps):
            # Selecionar ação
            action = self.act(state, training=True)
            
            # Converter ação em alocação de portfolio
            allocation = self._action_to_allocation(action, env)
            
            # Executar ação no ambiente
            next_state, reward, done, info = env.step(allocation)
            
            # Armazenar no replay buffer
            self.remember(state, action, reward, next_state, done)
            
            episode_reward += reward
            state = next_state
            
            # Treinar com minibatch
            self.replay(batch_size)
            
            if done:
                break
        
        self.training_episodes += 1
        self.episode_rewards.append(episode_reward)
        
        return episode_reward
    
    def _action_to_allocation(self, action: int, env) -> Dict[str, float]:
        """Converte índice de ação em alocação de portfolio.
        
        Args:
            action: Índice da ação
            env: Ambiente
            
        Returns:
            Dicionário com alocação de portfolio
        """
        # Implementação simplificada
        # Em produção, usar mapeo mais sofisticado
        
        n_sectors = 5  # Número de setores
        
        # Criar alocação baseada na ação
        allocation = {}
        base_weight = 1.0 / n_sectors
        
        for i in range(n_sectors):
            if i == action % n_sectors:
                allocation[f'sector_{i}'] = base_weight * 1.5
            else:
                allocation[f'sector_{i}'] = base_weight * 0.875
        
        # Normalizar
        total = sum(allocation.values())
        allocation = {k: v/total for k, v in allocation.items()}
        
        return allocation
    
    def train(self, env, episodes: int = 100,
             max_steps: int = 1000,
             batch_size: int = 32,
             eval_frequency: int = 10) -> List[float]:
        """Treina agente por múltiplos epísodios.
        
        Args:
            env: Ambiente
            episodes: Número de epísodios
            max_steps: Máximo de passos por epísodio
            batch_size: Tamanho do minibatch
            eval_frequency: Frequência de avaliação
            
        Returns:
            Lista de recompensas por epísodio
        """
        rewards_history = []
        
        for episode in range(episodes):
            episode_reward = self.learn_episode(env, max_steps, batch_size)
            rewards_history.append(episode_reward)
            
            if (episode + 1) % eval_frequency == 0:
                avg_reward = np.mean(rewards_history[-eval_frequency:])
                print(f"Episode {episode + 1}/{episodes} - Avg Reward: {avg_reward:.4f} - Epsilon: {self.epsilon:.4f}")
        
        return rewards_history
    
    def infer(self, state: np.ndarray) -> int:
        """Usa agente para fazer inferência (sem explorarção).
        
        Args:
            state: Estado atual
            
        Returns:
            Ação recomendada
        """
        return self.act(state, training=False)
    
    def get_stats(self) -> Dict[str, float]:
        """Retorna estatísticas de treinamento.
        
        Returns:
            Dicionário com estatsísticas
        """
        if len(self.episode_rewards) == 0:
            return {}
        
        returns = np.array(self.episode_rewards)
        
        return {
            'total_episodes': self.training_episodes,
            'mean_reward': np.mean(returns),
            'std_reward': np.std(returns),
            'max_reward': np.max(returns),
            'min_reward': np.min(returns),
            'epsilon': self.epsilon,
        }


if __name__ == "__main__":
    # Teste rápido
    agent = RLAgent(state_size=10, action_size=5)
    print(f"RLAgent criado com sucesso!")
    print(f"State size: {agent.state_size}")
    print(f"Action size: {agent.action_size}")
    print(f"Epsilon inicial: {agent.epsilon}")
    print(f"Learning rate: {agent.learning_rate}")
