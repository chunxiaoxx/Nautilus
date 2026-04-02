# Nautilus 可用API清单

**更新时间**: 2026-03-11
**状态**: 已验证可用

---

## 🎯 API分类

### 1. Google Gemini API (3个Key)

**API Key 1**: `AIzaSyAbLcIXvJiAzKJ-ntW6Jmcd8KcW_LPkz0Y`
**API Key 2**: `AIzaSyCpI9J-IBsBjIn6riby1LW5g7y9jsqImHc`
**API Key 3**: `AIzaSyDC016p_xAr0CID4d-8gi3-xJ7INyuQwXA`
**可用功能**:
- ✅ Gemini 3 Pro (文本对话)
- ✅ Gemini 3 Flash (文本对话)
- ✅ nano-banana 2 (图片生成) - 1.8MB PNG
- ✅ 图像理解
- ✅ 音频理解
- ✅ 长上下文 (1M tokens)
- ✅ JSON输出
- ✅ Function Calling

**用途**:
- PPT内容生成
- 图片生成
- 文本处理
- 数据分析

---

### 2. MiniMax API (2个Key - TTS语音合成)

**API Key 1**: `sk-api-OiN_Aul8KWBpqBcjLYF4L0jzcbq0PnCT2ykEcJJwaKUhTGopv2LppDrU2DF0GBLXUi0_fLsycxp8IkTsLoww4IyV8wo0uLOIh3dlhtqQuHYBO9QCkjXTfRA`

**API Key 2**: `sk-api-3e1uc2B5OuLsa5qRsF8lo3uQP99tZ5vnNPbGIf-Tt835rBsNTVMIY0IO7cI05o0CVpiznQ50EUotgmevZfFIRrVUsgL-ORK_VuL3kMgOm6_DFFX4EE2uhXA`

**文档**: https://platform.minimaxi.com/docs/api-reference/api-overview

**可用功能**:
- ✅ TTS (文字转语音)
- ✅ 中文语音合成
- ✅ 英文语音合成

**用途**:
- 路演演讲音频
- Demo视频配音
- 语音介绍

---

### 3. Manus.im API

**API Key**: `sk-gcUS0mbdfL4w1B8Qt7xBUMjtpEs2GCqGKs3-Ip08jUbafbzEj6PNNPVcNGfjHiSoRapUObaJD0QcLdE8-UySVGq088NQ`

**可用功能**:
- ✅ AI任务处理
- ✅ 自动化工作流

**用途**:
- 自动化任务
- 批量处理

---

### 4. 搜索API

**Serper API**: `d791032c27b9f99cdd02490b3fb49f10fad1bea9`
**Brave Search API**: `BSAvnW3gJQHXjujnsCcuYlJOkJqHqw-`

**可用功能**:
- ✅ 网页搜索
- ✅ 实时信息

**用途**:
- 市场研究
- 竞争对手分析
- 投资人信息

---

### 5. Firecrawl API

**API Key**: `fc-edaca1b274e746e5852d4f970cc9211b`

**可用功能**:
- ✅ 网页抓取
- ✅ 内容提取

**用途**:
- 投资人网站信息
- 市场数据收集

---

## 🚀 PPT生成方案

### 方案A: 使用Gemini API生成PPT内容

**优势**:
- 可以生成高质量文本
- 可以生成图片 (nano-banana 2)
- 可以优化内容

**实现**:
1. 使用Gemini生成每页内容
2. 使用nano-banana生成配图
3. 使用Python-PPTX组装

---

### 方案B: 使用现有Python脚本 + Gemini优化

**流程**:
1. 运行Python脚本生成基础PPT
2. 使用Gemini优化文字内容
3. 使用nano-banana生成图片
4. 手动插入图片

---

## 💡 推荐方案

### 立即可执行: Python脚本 + Gemini图片

**步骤**:

1. **生成基础PPT** (已完成)
```bash
cd C:/Users/chunx/Projects/nautilus-core/docs
python generate_pitch_deck.py
```

2. **使用nano-banana生成图片**
   - Logo
   - 产品截图
   - 架构图
   - 数据可视化

3. **插入图片到PPT**
   - 手动或脚本自动插入

---

## 🎨 可以生成的图片

使用nano-banana 2 (Gemini API):

1. **封面背景**
   - 科技感背景
   - 蓝色渐变

2. **产品架构图**
   - Trinity Engine可视化
   - 三层架构示意图

3. **市场增长曲线**
   - 数据可视化
   - 增长趋势图

4. **团队照片占位符**
   - 专业头像
   - 团队合影

5. **愿景图**
   - 未来场景
   - Agent网络

---

## 📋 下一步行动

### 选项1: 立即生成PPT

```bash
# 1. 生成基础PPT
python generate_pitch_deck.py

# 2. 打开查看
start Nautilus_Pitch_Deck_CN.pptx
```

### 选项2: 使用Gemini增强

我可以创建脚本：
1. 调用Gemini API优化文字
2. 调用nano-banana生成图片
3. 自动插入到PPT

### 选项3: 创建完整自动化脚本

整合所有API：
- Gemini: 内容生成
- nano-banana: 图片生成
- Python-PPTX: PPT组装
- 一键生成完整PPT

---

## 🎯 我的建议

**最快方案**:
1. 现在运行Python脚本生成基础PPT (5分钟)
2. 手动添加Logo和关键图片 (30分钟)
3. 今天就可以发送给投资人

**最佳方案**:
1. 我创建Gemini集成脚本 (1小时)
2. 自动生成图片和优化内容
3. 明天完成专业PPT

---

**你想选择哪个方案？**

1. 立即运行Python脚本
2. 我创建Gemini集成脚本
3. 其他方案
