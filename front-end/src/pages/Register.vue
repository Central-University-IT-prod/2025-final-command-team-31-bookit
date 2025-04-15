<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const store = useAuthStore()

const login = ref<string>('')
const password = ref<string>('')
const role = ref<string>('')
const name = ref<string>('')
const surname = ref<string>('')
const second_name = ref<string>('')
const email = ref<string>('')
const contacts = ref<string>('')
        
const signUp = async () => {
  await store.registration(role.value, login.value, name.value, surname.value, second_name.value, password.value, email.value, contacts.value)
}

</script>

<template>
  <div class="signup">
    <form action="">
      <h2>Регистрация</h2>
      <div class="form-container">
        <div class="column-half">
          <div class="form-group">
            <p>Имя</p>
            <input v-model="name" required type="text" placeholder="Имя" />
          </div>
          <div class="form-group">
            <p>Отчество</p>
            <input v-model="second_name" type="text" placeholder="Отчество" />
          </div>
          <div class="form-group">
            <p>Контакты</p>
            <textarea v-model="contacts" required type="text" placeholder="Контакты"></textarea>
          </div>
          <div class="form-group">
            <p>Логин</p>
            <input v-model="login" required type="text" placeholder="Логин" />
          </div>
        </div>

        <div class="column-half">
          <div class="form-group">
            <p>Фамилия</p>
            <input v-model="surname" required type="text" placeholder="Фамилия" />
          </div>
          <div class="form-group">
            <p>Email</p>
            <input v-model="email" required type="email" placeholder="Email" />
          </div>
          <div class="form-group">
            <p>Роль</p>
            <select v-model="role" placeholder="Роль">
              <option value="GUEST">Гость</option>
              <option value="EMPLOYEE">Сотрудник/Партнёр</option>
            </select>
          </div>

          <div class="form-group">
            <p>Пароль</p>
            <input v-model="password" required type="password" placeholder="Пароль" />
          </div>
        </div>

        <div class="full-width">
          <input type="file" />
        </div>

        <div class="inline">
          <button type="button" @click="signUp">Зарегистрироваться</button>
          <RouterLink to="/login">Войти</RouterLink>
        </div>
      </div>
    </form>
  </div>
</template>

<style scoped lang="scss">
@import '../assets/variables.scss';

.signup {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;

  .column-half {
    float: left;
    width: 50%;
  }

  form {
    flex-direction: row;
    box-sizing: border-box;
    border-radius: 10px;
    padding: 20px;
    border: solid 1px $border;
    box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.2);
    background: $white;

    h2 {
      text-align: center;
      font-size: 26px;
      margin-bottom: 20px;
    }

    p {
      margin-top: 10px;
      margin-bottom: 3px;
    }

    input[type='text'],
    input[type='password'],
    input[type='email'],
    textarea,
    select {
      width: 250px;
      padding: 10px 15px;
      font-size: 16px;
      background: $white;
      border: solid 1px $border;
      border-radius: 5px;
    }

    textarea {
      resize: vertical;
    }

    button {
      border: none;
      color: $dark;
      background: $primary;
      padding: 10px;
      display: block;
      border-radius: 5px;
      transition: 0.1s ease-in-out;
      font-size: 18px;
      cursor: pointer;

      &:hover {
        background: darken($primary, 10%);
      }
    }

    .inline {
      margin-top: 20px;
      display: flex;
      column-gap: 10px;
      align-items: center;

      a {
        color: $dark;

        &:hover {
          text-decoration: underline;
        }
      }
    }
    .form-container {
      display: flex;
      flex-wrap: wrap;
    }

    .form-group {
      padding: 0 10px;
      margin-bottom: 15px;
    }

    .full-width {
      width: 100%;
      padding: 0 10px;
      margin-top: 10px;
    }
  }
}

@media (max-width: 768px) {
  .signup {
    form {
      width: 95%;
      padding: 15px;

      .column-half {
        width: 100%;
        float: none;
      }

      .form-container {
        flex-direction: column;
      }

      input[type='text'],
      input[type='password'],
      input[type='email'],
      textarea,
      select {
        width: 70%;
      }
    }
  }
}
</style>
