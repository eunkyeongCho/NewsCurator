<template>
  <div class="chatbot-box" :class="{ 'dark-mode': isDarkMode }">
    <h3>🤖 AI 뉴스비서 뉴비</h3>
    <div class="chat-history">
      <div v-for="(msg, idx) in chatHistory" :key="idx" :class="msg.type">
        <span v-if="msg.type === 'user'">🙋‍♂️</span>
        <span v-else>🤖</span>
        {{ msg.content }}
      </div>
    </div>
    <div class="chatbot-actions">
      <button type="button" @click="sendQuestion('기사 요약해줘')">안녕! 기사 요약해줘</button>
      <button type="button" @click="sendQuestion('기사의 출처를 알려줘')">기사의 출처를 알려줘</button>
      <button type="button" @click="resetChat">대화 초기화</button>
    </div>
    <form @submit="onSubmit">
      <input v-model="question" placeholder="질문을 입력하세요" autocomplete="off" />
      <button type="submit">전송</button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, inject } from 'vue';
import axios from 'axios';

const props = defineProps({
  articleId: {
    type: [String, Number],
    required: true,
  },
});

const isDarkMode = inject('isDarkMode');

const chatHistory = ref([]);
const question = ref("");

const sendQuestion = async (q) => {
  const content = q !== undefined ? q : question.value;
  if (!content.trim()) return; // 빈 문자열 방지
  chatHistory.value.push({ type: "user", content });
  try {
    const res = await axios.post(
      `http://localhost:8000/api/articles/${props.articleId}/chatbot/`,
      { question: content },
      { withCredentials: true }
    );
    console.log(res.data.history);
    chatHistory.value = res.data.history.map((m) => ({
      type: m.type === "human" ? "user" : "bot",
      content: m.content,
    }));
    question.value = "";
  } catch (e) {
    chatHistory.value.push({ type: "bot", content: "에러가 발생했습니다." });
  }
};

const resetChat = async () => {
  await axios.post(
    `http://localhost:8000/api/articles/${props.articleId}/chatbot/reset/`,
    {},
    { withCredentials: true }
  );
  chatHistory.value = [];
};

const onSubmit = (e) => {
  e.preventDefault();
  sendQuestion();
};

watch(() => props.articleId, () => {
  chatHistory.value = [];
});
</script>

<style scoped>
.chatbot-box {
  background: var(--c-card-bg);
  border-radius: 12px;
  box-shadow: 0 2px 8px var(--c-card-shadow);
  padding: 20px;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  color: var(--c-text);
  transition: background 0.3s, color 0.3s;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 10px;
  background: var(--c-hover);
  border-radius: 8px;
  padding: 10px;
  max-height: 250px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.user {
  align-self: flex-end;
  background: #e3f0ff;
  color: #1976d2;
  border-radius: 16px 16px 4px 16px;
  padding: 6px 12px;
  margin: 2px 0;
  max-width: 70%;
  word-break: break-word;
  transition: background 0.3s, color 0.3s;
}

.bot {
  align-self: flex-start;
  background: var(--c-card-bg);
  color: var(--c-text);
  border-radius: 16px 16px 16px 4px;
  padding: 6px 12px;
  margin: 2px 0;
  max-width: 70%;
  word-break: break-word;
  border: 1px solid var(--c-border);
  transition: background 0.3s, color 0.3s;
}

form {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

input {
  flex: 1;
  border-radius: 6px;
  border: 1px solid var(--c-border);
  padding: 8px;
  background: var(--c-card-bg);
  color: var(--c-text);
  transition: background 0.3s, color 0.3s;
}

.chatbot-actions {
  margin-bottom: 8px;
}

.chatbot-actions button {
  margin-right: 8px;
  background: var(--c-hover);
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  color: var(--c-text);
}

.chatbot-actions button:hover {
  background: var(--c-primary);
  color: #fff;
}

/* 다크모드 오버라이드 */
.dark-mode {
  background: var(--c-card-bg);
  color: var(--c-text);
}
.dark-mode .chat-history {
  background: #23272f;
}
.dark-mode .user {
  background: #2d3a4a;
  color: #90caf9;
}
.dark-mode .bot {
  background: #23272f;
  color: #fff;
  border-color: #333;
}
.dark-mode input {
  background: #23272f;
  color: #fff;
  border-color: #333;
}
.dark-mode .chatbot-actions button {
  background: #23272f;
  color: #fff;
}
.dark-mode .chatbot-actions button:hover {
  background: #1976d2;
  color: #fff;
}
</style> 