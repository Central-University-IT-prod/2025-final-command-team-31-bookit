<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { computed, ref } from 'vue'

const authStore = useAuthStore()
const name = computed(() => authStore.userInfo.user.name)
const second_name = computed(() => authStore.userInfo.user.secondname)
const contacts = computed(() => authStore.userInfo.user.contacts)
const login = computed(() => authStore.userInfo.user.login)
const email = computed(() => authStore.userInfo.user.email)
const role = computed(() => authStore.userInfo.user.role)
const surname = computed(() => authStore.userInfo.user.surname)

const pName = ref<string>(name.value)
const pSecondName = ref<string>(second_name.value)
const pContacts = ref<string>(contacts.value)
const pLogin = ref<string>(login.value)
const pEmail = ref<string>(email.value)
const pRole = ref<string>(role.value)
const pSurname = ref<string>(surname.value)


const patchData = async () => {
  await authStore.patchData(pRole.value, pLogin.value, pName.value, pSurname.value, pSecondName.value, pEmail.value, pContacts.value)
}

</script>

<template>
  <div class="main">
    <form action="">
      <h1>Основные данные</h1>
      <h2>Личные данные</h2>
      <div class="form-container">
        <div class="column-half">
          <div class="form-group">
            <p>Имя</p>
            <input v-model="pName" type="text" :placeholder="name" />
          </div>
          <div class="form-group">
            <p>Отчество</p>
            <input v-model="pSecondName" type="text" :placeholder="second_name" />
          </div>
          <div class="form-group">
            <p>Контакты</p>
            <textarea v-model="pContacts" type="text" :placeholder="contacts"></textarea>
          </div>
          <div class="form-group">
            <p>Логин</p>
            <input v-model="pLogin" type="text" :placeholder="login" />
          </div>
        </div>

        <div class="column-half">
          <div class="form-group">
            <p>Фамилия</p>
            <input v-model="pSurname" type="text" :placeholder="surname" />
          </div>
          <div class="form-group">
            <p>Email</p>
            <input v-model="pEmail" type="email" :placeholder="email" />
          </div>
          <div class="form-group">
            <p>Роль</p>
            <select v-model="pRole" :placeholder="role">
              <option value="GUEST">Гость</option>
              <option value="EMPLOYEE">Сотрудник/Партнёр</option>
            </select>
          </div>

          <!-- <div class="form-group">
            <p>Пароль</p>
            <input v-model="password" required type="password" placeholder="Пароль" />
          </div> -->
        </div>

        <div class="full-width">
          <input type="file" />
        </div>
      </div>
      <button type="button" @click="patchData">Сохранить</button>
    </form>
  </div>
</template>

<style lang="scss">
@import '../../assets/components/account.scss';
@import '../../assets/variables.scss';

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

@media (max-width: 768px) {
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
</style>
