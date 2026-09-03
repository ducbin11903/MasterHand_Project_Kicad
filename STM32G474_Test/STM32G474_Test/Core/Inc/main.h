/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32g4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define DIAG_T2_Pin GPIO_PIN_13
#define DIAG_T2_GPIO_Port GPIOC
#define DIAG_T1_Pin GPIO_PIN_14
#define DIAG_T1_GPIO_Port GPIOC
#define DIAG_I_Pin GPIO_PIN_15
#define DIAG_I_GPIO_Port GPIOC
#define PWMA_T2_Pin GPIO_PIN_0
#define PWMA_T2_GPIO_Port GPIOC
#define PWMB_T2_Pin GPIO_PIN_1
#define PWMB_T2_GPIO_Port GPIOC
#define PWMA_T1_Pin GPIO_PIN_2
#define PWMA_T1_GPIO_Port GPIOC
#define PWMB_T1_Pin GPIO_PIN_3
#define PWMB_T1_GPIO_Port GPIOC
#define ECA_T2_Pin GPIO_PIN_0
#define ECA_T2_GPIO_Port GPIOA
#define ECB_T2_Pin GPIO_PIN_1
#define ECB_T2_GPIO_Port GPIOA
#define OCM_T2_Pin GPIO_PIN_2
#define OCM_T2_GPIO_Port GPIOA
#define OCM_T1_Pin GPIO_PIN_3
#define OCM_T1_GPIO_Port GPIOA
#define ECC_T2_Pin GPIO_PIN_4
#define ECC_T2_GPIO_Port GPIOA
#define ECC_T1_Pin GPIO_PIN_5
#define ECC_T1_GPIO_Port GPIOA
#define ECA_T1_Pin GPIO_PIN_6
#define ECA_T1_GPIO_Port GPIOA
#define ECB_T1_Pin GPIO_PIN_7
#define ECB_T1_GPIO_Port GPIOA
#define ECC_I_Pin GPIO_PIN_4
#define ECC_I_GPIO_Port GPIOC
#define SENSE_VBAT_Pin GPIO_PIN_5
#define SENSE_VBAT_GPIO_Port GPIOC
#define OCM_I_Pin GPIO_PIN_0
#define OCM_I_GPIO_Port GPIOB
#define EN_I_Pin GPIO_PIN_1
#define EN_I_GPIO_Port GPIOB
#define BOARD_VERSION_Pin GPIO_PIN_2
#define BOARD_VERSION_GPIO_Port GPIOB
#define EN_IB10_Pin GPIO_PIN_10
#define EN_IB10_GPIO_Port GPIOB
#define PWMA_I_Pin GPIO_PIN_14
#define PWMA_I_GPIO_Port GPIOB
#define PWMB_I_Pin GPIO_PIN_15
#define PWMB_I_GPIO_Port GPIOB
#define ECA_I_Pin GPIO_PIN_6
#define ECA_I_GPIO_Port GPIOC
#define ECB_I_Pin GPIO_PIN_7
#define ECB_I_GPIO_Port GPIOC
#define LED_DEBUG_Pin GPIO_PIN_10
#define LED_DEBUG_GPIO_Port GPIOA
#define LED_T2_Pin GPIO_PIN_15
#define LED_T2_GPIO_Port GPIOA
#define LED_T1_Pin GPIO_PIN_10
#define LED_T1_GPIO_Port GPIOC
#define LED_I_Pin GPIO_PIN_11
#define LED_I_GPIO_Port GPIOC
#define MCU_ID_Pin GPIO_PIN_12
#define MCU_ID_GPIO_Port GPIOC
#define EN_T1_Pin GPIO_PIN_2
#define EN_T1_GPIO_Port GPIOD
#define PWM_BUZZER_Pin GPIO_PIN_9
#define PWM_BUZZER_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
