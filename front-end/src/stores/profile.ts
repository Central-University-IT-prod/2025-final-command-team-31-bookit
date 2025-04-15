import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useProfileStore = defineStore('profile', () => {
    const currentStep = ref(0)



    function setCurrentStep(step: number) {
        currentStep.value = step
      }

    return { currentStep, setCurrentStep}
})

