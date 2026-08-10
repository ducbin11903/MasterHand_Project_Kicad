# CyberHand — Motor Control & Main Board — Project Summary
_Cập nhật: 2026-07-14 · Dùng làm context cho Cowork / tài liệu repo_

---

## 1. Mô tả ngắn

Thiết kế 2 PCB cho bàn tay robot humanoid (CyberHand/CyberTUM) dùng 6 motor DC gear JGA12-N20B 6V: **Motor Control Board** và **MainBoard**, giao tiếp CAN FD + RS-422. Công cụ: **KiCad 9.0.1** + Git, hierarchy schematic, multi-channel reuse. Schematic đang vẽ theo cấu trúc sheet đánh số (vd sheet 6/19: "Power - Generation").

---

## 2. Hardware

### Motor Control Board
- 2× STM32G474RET6 (LQFP64, 170MHz), mỗi MCU điều khiển 3 motor
- 6× TB9051FTG H-bridge (VM 4.5–28V, 5A peak, AEC-Q100)
- 6× JGA12-N20B DC gear motor (stall 0.55A @6V, R cuộn ≈ 11Ω)
- 6× SS49E linear Hall sensor (ratiometric, cấp +A3V3)
- 2× TJA1051T CAN FD transceiver (VCC 5V), 120Ω termination 2 đầu bus
- 2× MAX3491 RS-422 transceiver (3.3V)
- 2× SHT31 (I2C 0x44, mỗi MCU 1 con)
- 2× USB Type-C riêng (DFU + CDC mỗi MCU) — **không nối VBUS vào rail 5V**, chỉ sense qua divider
- Crystal 8MHz HSE ×2, buzzer, 6× motor LED, battery voltage sensing

### MainBoard
- 1× STM32G474RET6, TCA9548A I2C mux, 5× FSR, ICM42688P IMU, 5× SK6812, TJA1051T, W5500 (SPI), crystal 32.768kHz

---

## 3. Power Architecture (ĐÃ CẬP NHẬT — thay thế plan LD39200 cũ)

```
LiPo 2S 7.4V / 2200mAh / 10C  (6.6–8.4V)
    │
[Polyfuse 15A] → [STPS20L60S Schottky] → [SMBJ10CA TVS]
    │
[BULK 330µF/25V polymer, ESR 20–40mΩ]  ← quyết định mới, xem mục 5
    │
    ├── +VBAT → 6× TB9051FTG VM  (+ 6× 10µF 1206 sát chân VM từng driver)
    │
    ├── U3 TPSM63603RDHR (buck module, 3A) → +5V
    │       ├── Tải 5V trực tiếp: TB9051 VCC ×6, TJA1051T ×2, LED/buzzer
    │       ├── U4 TPS62162DSG + L 2.2µH (buck 1A) → +3V3 (digital)
    │       │       └── STM32 ×2, MAX3491 ×2, SHT31, logic phụ
    │       └── U5 TLV75533PDBVR (LDO 500mA) → +A3V3 (analog)
    │               └── SS49E ×6, VDDA/VREF+ ×2, (SHT31 nếu chuyển sang analog rail)
```

Lý do kiến trúc 3 regulator: 3V3 digital từ buck (hiệu suất), A3V3 từ LDO riêng (sạch cho ADC).
SS49E ratiometric + VREF+ cùng rail A3V3 → sai số nguồn tự triệt tiêu.

### Việc còn phải xác nhận trên sheet Power - Generation (6/19)
- [ ] **FB pin TPS62162 (bản fixed 3.3V) phải nối GND** — không để floating
- [ ] Xác nhận net **F_VIN_3V3 lấy từ +5V** (TLV75533 VIN max 5.5V, không được ăn VBAT)
- [ ] Nối **VLDOIN (pin 22) của TPSM63603 → VOUT** (VOUT=5V ≥ 3.3V, tăng hiệu suất)
- [ ] Tính divider R1/R4 trên EN/SYNC cho **UVLO ≈ 6.0–6.2V** (bảo vệ LiPo, có hysteresis)
- [ ] **EN_3V3 lấy từ PG của U3** (pull-up 100k lên 5V, PG open-drain) → sequencing 5V trước, 3V3+A3V3 sau
- [ ] Điền value tụ: U3 in 2×10µF/25V + 100nF; U3 out 3–4×22µF/10V (theo bảng datasheet ứng R5/RT); VCC 1µF; CBOOT 100nF+RBOOT; U4 in 10µF/out 22µF, L1 Isat ≥ 1.5A; U5 in/out 1µF (out 10µF càng tốt)
- [ ] FB4 sau LDO: giữ thì thêm 10µF+100nF tại VDDA/VREF+; bỏ cũng được
- [ ] AGND của U3 nối PGND single-point theo layout guideline TI

---

## 4. Power Budget (ĐÃ TÍNH LẠI)

Phương pháp: I_avg = Σ Typ tại điều kiện thật; I_peak = Σ Max @T_max, chỉ tải đồng thời. Chọn regulator ≥ 1.5–2× peak.

| Rail | Nguồn | Avg (typ) | Peak (max) | Định mức | Ghi chú |
|---|---|---|---|---|---|
| VBAT 7.4V | LiPo qua protection | ~1.25A | ~3.75A (duty≤71%) / **4.6A nếu duty 100% @8.4V** | 22A (10C) | 6 motor stall = worst case |
| +5V | TPSM63603 | ~180mA | ~610mA | 3A | TB9051 VCC + TJA1051 dominant + đầu vào U4/U5 |
| +3V3 | TPS62162 | ~113mA | ~340mA | 1A | STM32 ×2 (~60mA max/con gồm peripheral+analog) + MAX3491 TX |
| +A3V3 | TLV75533 | ~40mA | ~67mA | 500mA | **Sửa budget cũ 8.3/15.6mA — thiếu SS49E ~6mA/con** |

Ghi chú quan trọng:
- **Stall N20 scale theo áp**: 0.55A là @6V. Full duty @8.4V → 0.77A/motor. Quyết định: giới hạn duty max ≈ 71% trong firmware HOẶC tính budget theo 4.6A. Ghi giả định vào tài liệu.
- STM32G474: I_DD bảng datasheet đo "all peripherals disabled" — phải cộng Table 35 (peripheral µA/MHz: TIM1/8 ~10.8, FDCAN 22.2, ADC 6.2...) ≈ +13mA @170MHz, và analog (OPAMP 1.3–2.2mA/con, ADC I_DDA...) ≈ +6mA. Tổng thực tế ~60mA max/con @85°C.
- MAX3491: I_CC datasheet KHÔNG gồm dòng lái bus (±2V/120Ω ≈ 20–33mA, cộng riêng). TJA1051: ĐÃ gồm, lấy hàng dominant (~70mA max) cho peak.
- LED: dòng do điện trở chọn, không lấy từ datasheet LED.

---

## 5. Bulk cap VBAT (quyết định + phương pháp)

**Chọn: 1× polymer 330µF / 16–25V, ESR 20–40mΩ** (kiểu OS-CON/SP-Cap) ngay sau Schottky, + 6× 10µF ceramic 1206 sát VM từng TB9051.

Cơ sở tính (L_lead ≈ 0.5µH, ΔI = 3.3A, ΔV cho phép ≈ 0.3V):
- C ≥ L·(ΔI/ΔV)² = 0.5µ × (3.3/0.3)² ≈ 60µF tối thiểu → ×3–5 margin → 330µF
- ESR_opt ≈ √(L/C) = √(0.5µ/330µ) ≈ 39mΩ (damping ζ ≈ 0.5–1; toàn ceramic ESR 2mΩ sẽ ringing)
- Ripple rating ≥ ~1A RMS @100kHz; voltage rating 25V (TVS clamp ~17V)

Mô phỏng (load step 0→3.3A qua 0.5µH, pin 40mΩ + polyfuse + Schottky):
| Cấu hình | Vmin tại board | Kết quả |
|---|---|---|
| Chỉ 30µF ceramic | 6.59V | droop 0.46V + ringing mạnh |
| +100µF/50mΩ | 6.84V | ổn |
| **+330µF/30mΩ polymer** | **6.89V** | **droop 0.16V, tắt gọn — CHỌN** |
| +330µF ceramic 2mΩ | 6.88V | droop OK nhưng ring kéo dài |

File mô phỏng trong repo/tài liệu: `bulk_cap_vbat.cir` (LTspice/ngspice), `bulk_cap_sim.py`. Validate board thật: load step + oscilloscope với ground spring tại chân tụ.

---

## 6. Firmware STM32G474 — Motor Control (không đổi)

- TIM1/TIM8 → PWM 20kHz ×6 motor; **duty max ≈ 71% nếu chọn phương án giới hạn stall**
- TIM2/3/4 → encoder mode; TIM6 → control loop 20kHz
- ADC injected trigger từ TIM1, simultaneous ADC1+ADC2 đọc OCM
- OPAMP + COMP → TIM1 BKIN (hardware overcurrent)
- FDCAN1 1Mbps (3 node), DMA (ADC circular, UART TX), EXTI (DIAG, S_ENC)
- I2C SHT31 (0x44), USB CDC/DFU (PA11/PA12), HSE 8MHz, CRC hardware

---

## 7. Giao tiếp giữa các board (không đổi)

MainBoard ↔ CAN FD 1Mbps ↔ Motor Control (MCU1+MCU2); RS-422; Ethernet/W5500 → ROS2.
CAN: 3 node, 3× TJA1051T, 1 bus CANH/CANL, 120Ω tại 2 đầu vật lý.

---

## 8. KiCad & Git

- KiCad 9.0.1, Git version control, mỗi sub-sheet 1 file riêng
- Cấu trúc: `CyberHand/{Motor_Control, Main_Board, Library, Datasheets}` — sheets/ chứa Power_Source, Motor_Driver (×6 reuse), Motor_Controller_1/2, CAN_Transceiver, RS422, Hall_Sensor, SHT31
- `.gitignore`: `*.kicad_prl`, `*-backups/`, `fp-info-cache`
- Commit convention: `[MOTOR] ...`, `[MAIN] ...`

---

## 9. Trạng thái hiện tại

### Motor Control Board
- ✅ Block diagram, component selection
- ✅ Power budget — **đã tính lại theo mục 4**
- ✅ Power - Generation schematic (sheet 6/19) draft — **còn checklist mục 3**
- ✅ Motor Driver sub-sheet draft (TB9051FTG), MCU schematic draft
- ✅ Bulk cap: đã chọn + mô phỏng (mục 5)
- ⬜ Hoàn thiện Power path protection sub-sheet (Polyfuse + Schottky + TVS + bulk 330µF)
- ⬜ CAN transceiver sub-sheet, RS-422 sub-sheet, Hall SS49E sub-sheet, SHT31 sub-sheet
- ⬜ PCB layout (note: FB trace tránh SW node, minimize SW loop, AGND single-point)

### MainBoard
- ✅ Block diagram
- ⬜ Schematic, PCB layout

---

## 10. Tham khảo nhanh

```
Motor:      JGA12-N20B 6V, stall 0.55A @6V (0.77A @8.4V full duty), R ≈ 11Ω
Driver:     TB9051FTG, VM 4.5–28V, 5A peak, VCC 5V (UV detect 3.5V)
MCU:        STM32G474RET6, 170MHz boost, ~60mA max thực tế/con @85°C
Buck 5V:    TPSM63603RDHR, 3A — nối VLDOIN→VOUT, UVLO qua EN divider ≈ 6.0V
Buck 3V3:   TPS62162DSG, 1A, L 2.2µH, FIXED → FB nối GND
LDO A3V3:   TLV75533PDBVR, 500mA, VIN max 5.5V (chỉ ăn từ +5V)
CAN:        TJA1051T, dominant ~70mA max (đã gồm bus drive)
RS-422:     MAX3491 — I_CC chưa gồm dòng lái bus (+20–33mA/driver khi TX)
Hall:       SS49E ratiometric, ~6mA typ/10mA max mỗi con, cấp A3V3
Bulk:       Polymer 330µF/25V ESR 20–40mΩ + 6×10µF sát VM
Nguồn:      LiPo 2S 7.4V/2200mAh/10C, protection: Polyfuse 15A + STPS20L60S + SMBJ10CA
Sequencing: VBAT → 5V → (PG U3) → 3V3 + A3V3
```
