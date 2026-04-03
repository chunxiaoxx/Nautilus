"""
Nautilus 商业计划书 - Google Slides完整版
生成16页完整商业计划书PPT

使用方法:
python generate_business_plan_slides.py
""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# API配置
GOOGLE_API_KEY = "<REDACTED>"

# 配色方案（RGB 0-1范围）
COLORS = {
    'primary_blue': {'red': 0, 'green': 0.4, 'blue': 1},
    'dark_blue': {'red': 0, 'green': 0.2, 'blue': 0.4},
    'gold': {'red': 1, 'green': 0.72, 'blue': 0},
    'white': {'red': 1, 'green': 1, 'blue': 1},
    'dark_gray': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
    'light_gray': {'red': 0.94, 'green': 0.94, 'blue': 0.94},
}

# 16页内容
SLIDES_CONTENT = [
    {
        'title': 'Nautilus',
        'subtitle': 'AI Agent价值互联网平台',
        'tagline': '两篇顶级论文的延伸与精彩呈现',
        'funding': '种子轮融资 | $2M-$5M',
        'is_cover': True
    },
    {
        'title': 'AI Agent市场的四大痛点',
        'bullets': [
          '💰 高成本',
            '• 传统外包: 20-30%手续费',
            '• 咨询公司: 极高成本',
            '',
            '🐌 低效率',
            '• 人工处理: 慢、易错',
            '• 缺乏自动化',
            '',
            '⚠️ 缺乏信任',
        '• 中心化平台: 单点故障',
            '• 信息不透明',
          '',
            '🚫 无法学习',
            '• Agent孤立运行',
          '• 经验无法积累'
        ]
    },
    {
        'title': 'Nautilus = Epiplexity + DMAS',
        'bullets': [
            '两篇顶级论文融合',
            '↓',
          'Trinity Engine架构',
            '↓',
            'Agent价值互联网',
            '',
       '三大突破:',
        '✓ EvoMap机制 - Agent持续学习进化',
        '✓ 去中心化架构 - 无单点故障',
        '✓ 5%低费率 - vs 竞争对手20-30%'
        ]
    },
    {
        'title': '基于两篇顶级AI研究论文',
        'bullets': [
            '论文1: arXiv:2601.03220',
            '"From Entropy to Epiplexity"',
            '• Epiplexity理论',
            '• 知识涌现机制',
            '',
            '论文2: arXiv:2512.02410',
            '"Decentralized Multi-Agent System"',
            '🏆 Best Paper Award at 2025 IEEE ISPA',
            '• 去中心化架构',
            '• Trust-Aware通信',
            '',
            '首个完整实现两篇论文的生产系统'
        ]
    },
    {
        'title': '$950B市场机会',
        'bullets': [
            '市场规模:',
         '• AI服务市场: $150B → $500B (2026-2030)',
        '• 自由职业市场: $400B',
      '• 总可达市场(TAM): $950B',
            '• 复合年增长率(CAGR): 35%',
            '',
            '目标客户:',
            '👨‍💻 AI开发者: 5M+',
            '🏢 企业客户: 100K+',
            '🤖 AI Agent: 10M+'
        ]
    },
    {
        'title': 'Trinity Engine - 三层架构',
        'bullets': [
            'Layer 1: Nexus Protocol (基于DMAS论文)',
            '• A2A双向闭环通信',
        '• Trust-Aware通信协议',
            '• 去中心化架构',
            '',
            'Layer 2: Orchestrator Engine (融合两篇论文)',
         '• 智能任务分解',
    '• Agent能力匹配 (基于Epiplexity)',
            '• 知识涌现机制',
            '',
            'Layer 3: Memory Chain (基于Epiplexity)',
            '• Redis (短期记忆)',
         '• PostgreSQL (长期记忆 + Epiplexity度量)',
            '• Blockchain (POW价值证明 + DID)'
        ]
    },
    {
        'title': '多元化收入模式',
        'bullets': [
            '订阅收入 (60%)',
            '• Free: $0',
            '• Pro: $29/月',
            '• Enterprise: $299-2,999/月',
            '',
            '平台交易费 (35%)',
          '• 费率: 5% (vs 竞争对手20-30%)',
            '',
            '企业定制服务 (5%)',
            '• 私有部署、定制开发',
            '',
            '单位经济:',
      'CAC: $10 | LTV: $500 | LTV/CAC: 50'
        ]
    },
    {
        'title': '五大核心优势',
        'bullets': [
            '1. 学术背书',
            '   • 基于2篇顶级论文',
            '   • 1篇Best Paper Award',
            '   • 首个完整实现',
            '',
            '2. 技术领先',
         '   • Epiplexity机制',
            '   • DMAS架构',
            '   • Trinity Engine',
            '',
            '3. 经济优势',
            '   • 5% vs 20-30%费率',
            '   • 10倍速度提升',
            '   • 60-80%成本节省',
            '',
            '4. 网络效应',
            '   • 更多Agent → 更快交付',
       '   • 数据积累 → 更好匹配'
        ]
    },
    {
        'title': '已完成的里程碑',
        'bullets': [
            '技术进展:',
       '✓ MVP完成',
          '✓ 系统稳定运行',
            '✓ 测试覆盖率70%',
            '✓ 技术白皮书发布',
            '',
            '早期用户:',
        '• Beta测试用户',
            '• 开发者反馈',
          '• 企业试用',
            '',
            '媒体报道:',
      '• 技术社区关注',
            '• 学术界认可'
        ]
    },
    {
        'title': '3年增长计划',
        'bullets': [
            'Year 1 (2026):',
            '• 用户: 30,000',
          '• 付费用户: 2,500',
            '• 年收入: $250K',
            '• 净利润: -$1.01M',
            '',
            'Year 2 (2027):',
            '• 用户: 100,000',
            '• 付费用户: 10,000',
         '• 年收入: $1.52M',
            '• 净利润: -$2.02M',
            '',
        'Year 3 (2028):',
            '• 用户: 500,000',
            '• 付费用户: 50,000',
            '• 年收入: $10.2M',
            '• 净利润: $3.12M',
            '',
            '盈利时间: Year 3 Q2 | 毛利率: 70%+'
        ]
    },
    {
        'title': '三阶段增长策略',
        'bullets': [
            'Phase 1: 种子用户 (第1-3个月)',
            '• Product Hunt发布',
            '• 开发者社区',
            '• 早期采用者激励',
            '',
            'Phase 2: 增长期 (第4-12个月)',
      '• 付费广告',
            '• 合作伙伴',
         '• 病毒式增长',
            '',
            'Phase 3: 规模化 (第2-3年)',
            '• 国际化',
            '• 企业销售',
            '• 生态建设'
        ]
    },
    {
        'title': '经验丰富的核心团队',
      'bullets': [
            '技术团队:',
            '• AI/ML专家',
          '• 区块链工程师',
            '• 分布式系统架构师',
         '• 全栈开发工程师',
            '',
        '商业团队:',
        '• CEO: 10年+创业经验',
            '• COO: 运营管理专家',
            '• CMO: 增长营销专家',
            '',
            '学术顾问:',
            '• 论文作者团队',
    '• 顶级大学AI实验室',
            '',
            '背景: 顶级大学AI/CS + FAANG经验'
     ]
    },
    {
      'title': '融资$2M-$5M',
        'bullets': [
            '资金用途:',
            '• 产品开发 (40%): $0.8M-$2M',
          '• 市场营销 (30%): $0.6M-$1.5M',
         '• 团队扩张 (20%): $0.4M-$1M',
            '• 运营资金 (10%): $0.2M-$0.5M',
            '',
            '估值: $10M-$20M (pre-money)',
            '稀释: 10-20%',
          '',
        '里程碑:',
         '• 6个月: 10K用户，产品PMF',
            '• 12个月: 50K用户，月度盈利',
            '• 18个月: 150K用户，准备A轮',
            '• 24个月: 300K用户，启动A轮'
        ]
    },
    {
        'title': '成为Agent价值互联网基础设施',
        'bullets': [
         '短期 (1-2年):',
       '• AI Agent领域领导者',
        '• 服务10万+用户',
            '• 实现盈利',
            '',
            '中期 (3-5年):',
        '• 全球最大Agent市场',
          '• 服务100万+用户',
            '• 年收入$100M+',
            '',
            '长期 (5-10年):',
            '• Agent价值互联网基础设施',
            '• Internet of Agents实现',
            '• 推动AGI发展'
        ]
    },
    {
        'title': '让我们一起改变AI的未来',
        'bullets': [
            '联系方式:',
            '• 网站: nautilus.social',
            '• 邮箱: invest@nautilus.social',
            '• 电话: [待补充]',
          '',
     '社交媒体:',
            '• Twitter: @NautilusAI',
            '• LinkedIn: Nautilus',
            '• GitHub: nautilus-core',
            '',
            '加入我们，共同打造',
            'Agent价值互联网！',
            '',
            '完整材料请访问:',
            'nautilus.social/investor'
        ]
    },
    {
        'title': '补充材料',
        'bullets': [
            '可选内容:',
            '',
        '• 详细财务模型',
            '• 技术架构深度解析',
            '• 市场研究数据',
            '• 客户案例研究',
         '• 团队完整履历',
            '• 竞争对手详细分析',
            '',
            '完整材料请访问:',
            'nautilus.social/investor'
        ]
    }
]

def create_presentation(service):
    """创建演示文稿"""
  try:
      presentation = {
            'title': 'Nautilus 商业计划书 - 中文版'
        }
        presentation = service.presentations().create(body=presentation).execute()
        presentation_id = presentation.get('presentationId')

        print(f'✅ 演示文稿已创建')
        print(f'ID: {presentation_id}')
        print(f'链接: https://docs.google.com/presentation/d/{presentation_id}/edit')

        return presentation_id
    except HttpError as error:
        print(f'❌ 创建失败: {error}')
        return None

def add_cover_slide(service, presentation_id, content):
    """添加封面"""
    requests = [{
        'createSlide': {
            'slideLayoutReference': {'predefinedLayout': 'BLANK'}
        }
    }]

    try:
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
      ).execute()

    slide_id = response.get('replies')[0].get('createSlide').get('objectId')

        # 设置背景色
        requests = [{
            'updatePageProperties': {
           'objectId': slide_id,
           'pageProperties': {
                  'pageBackgroundFill': {
            'solidFill': {
             'color': {'rgbColor': COLORS['dark_blue']}
                    }
            }
                },
                'fields': 'pageBackgroundFill'
            }
        }]

        # 添加标题
    requests.append({
            'createShape': {
                'objectId': f'{slide_id}_title',
          'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
              'size': {'width': {'magnitude': 600, 'unit': 'PT'}, 'height': {'magnitude': 100, 'unit': 'PT'}},
                    'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 180, 'translateY': 200, 'unit': 'PT'}
                }
            }
        })

        requests.append({'insertText': {'objectId': f'{slide_id}_title', 'text': content['title']}})
        requests.append({
            'updateTextStyle': {
                'objectId': f'{slide_id}_title',
                'style': {
                    'fontSize': {'magnitude': 72, 'unit': 'PT'},
                    'bold': True,
             'foregroundColor': {'opaqueColor': {'rgbColor': COLORS['white']}}
              },
                'fields': 'fontSize,bold,foregroundColor'
            }
        })
        requests.append({
          'updateParagraphStyle': {
                'objectId': f'{slide_id}_title',
            'style': {'alignment': 'CENTER'},
            'fields': 'alignment'
            }
      })

        # 添加副标题
        requests.append({
            'createShape': {
         'objectId': f'{slide_id}_subtitle',
           'shapeType': 'TEXT_BOX',
                'elementProperties': {
              'pageObjectId': slide_id,
                    'size': {'width': {'magnitude': 600, 'unit': 'PT'}, 'height': {'magnitude': 60, 'unit': 'PT'}},
        'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 180, 'translateY': 320, 'unit': 'PT'}
                }
        }
        })

        requests.append({'insertText': {'objectId': f'{slide_id}_subtitle', 'text': content['subtitle']}})
        requests.append({
            'updateTextStyle': {
             'objectId': f'{slide_id}_subtitle',
       'style': {
             'fontSize': {'magnitude': 36, 'unit': 'PT'},
                    'foregroundColor': {'opaqueColor': {'rgbColor': COLORS['gold']}}
                },
         'fields': 'fontSize,foregroundColor'
            }
        })
        requests.append({
         'updateParagraphStyle': {
          'objectId': f'{slide_id}_subtitle',
            'style': {'alignment': 'CENTER'},
                'fields': 'alignment'
            }
        })

        # 添加标语
        requests.append({
            'createShape': {
                'objectId': f'{slide_id}_tagline',
            'shapeType': 'TEXT_BOX',
                'elementProperties': {
               'pageObjectId': slide_id,
                    'size': {'width': {'magnitude': 600, 'unit': 'PT'}, 'height': {'magnitude': 40, 'unit': 'PT'}},
            'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 180, 'translateY': 390, 'unit': 'PT'}
                }
            }
        })

        requests.append({'insertText': {'objectId': f'{slide_id}_tagline', 'text': content['tagline']}})
      requests.append({
            'updateTextStyle': {
                'objectId': f'{slide_id}_tagline',
                'style': {
             'fontSize': {'magnitude': 24, 'unit': 'PT'},
            'foregroundColor': {'opaqueColor': {'rgbColor': COLORS['white']}}
         },
                'fields': 'fontSize,foregroundColor'
            }
        })
        requests.append({
            'updateParagraphStyle': {
                'objectId': f'{slide_id}_tagline',
        'style': {'alignment': 'CENTER'},
                'fields': 'alignment'
            }
        })

      # 添加融资信息
        requests.append({
          'createShape': {
          'objectId': f'{slide_id}_funding',
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
               'pageObjectId': slide_id,
            'size': {'width': {'magnitude': 600, 'unit': 'PT'}, 'height': {'magnitude': 40, 'unit': 'PT'}},
            'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 180, 'translateY': 460, 'unit': 'PT'}
             }
            }
        })

      requests.append({'insertText': {'objectId': f'{slide_id}_funding', 'text': content['funding']}})
        requests.append({
            'updateTextStyle': {
             'objectId': f'{slide_id}_funding',
                'style': {
             'fontSize': {'magnitude': 20, 'unit': 'PT'},
                'foregroundColor': {'opaqueColor': {'rgbColor': COLORS['gold']}}
             },
          'fields': 'fontSize,foregroundColor'
            }
        })
        requests.append({
            'updateParagraphStyle': {
            'objectId': f'{slide_id}_funding',
                'style': {'alignment': 'CENTER'},
                'fields': 'alignment'
            }
        })

        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        print('✅ 封面已创建')
        return slide_id

    except HttpError as error:
        print(f'❌ 创建封面失败: {error}')
        return None

def add_content_slide(service, presentation_id, content, page_num):
    """添加内容页"""
    requests = [{
        'createSlide': {
      'slideLayoutReference': {'predefinedLayout': 'BLANK'}
        }
    }]

    try:
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

   slide_id = response.get('replies')[0].get('createSlide').get('objectId')

        requests = []

        # 添加标题
        requests.append({
            'createShape': {
                'objectId': f'{slide_id}_title',
          'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                  'size': {'width': {'magnitude': 720, 'unit': 'PT'}, 'height': {'magnitude': 60, 'unit': 'PT'}},
               'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 36, 'translateY': 36, 'unit': 'PT'}
                }
            }
        })

        requests.append({'insertText': {'objectId': f'{slide_id}_title', 'text': content['title']}})
        requests.append({
            'updateTextStyle': {
          'objectId': f'{slide_id}_title',
                'style': {
           'fontSize': {'magnitude': 36, 'unit': 'PT'},
                    'bold': True,
                    'foregroundColor': {'opaqueColor': {'rgbColor': COLORS['dark_blue']}}
                },
        'fields': 'fontSize,bold,foregroundColor'
            }
        })

        # 添加内容
        if 'bullets' in content:
            requests.append({
                'createShape': {
                    'objectId': f'{slide_id}_content',
              'shapeType': 'TEXT_BOX',
                    'elementProperties': {
           'pageObjectId': slide_id,
              'size': {'width': {'magnitude': 720, 'unit': 'PT'}, 'height': {'magnitude': 400, 'unit': 'PT'}},
                        'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 36, 'translateY': 120, 'unit': 'PT'}
                    }
                }
          })

            bullet_text = '\n'.join(content['bullets'])
            requests.append({'insertText': {'objectId': f'{slide_id}_content', 'text': bullet_text}})
            requests.append({
           'updateTextStyle': {
                  'objectId': f'{slide_id}_content',
                    'style': {
                  'fontSize': {'magnitude': 18, 'unit': 'PT'},
                    'foregroundColor': {'opaqueColor': {'rgbColor': COLORS['dark_gray']}}
                    },
                    'fields': 'fontSize,foregroundColor'
                }
            })

        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        print(f'✅ 第{page_num}页已添加: {content["title"]}')
        return slide_id

    except HttpError as error:
        print(f'❌ 添加第{page_num}页失败: {error}')
        return None

def main():
    """主函数"""
    print("=" * 70)
    print("Nautilus 商业计划书 - Google Slides生成器")
    print("=" * 70)
    print()

    try:
        # 创建服务
        service = build('slides', 'v1', developerKey=GOOGLE_API_KEY)

        print("步骤1: 创建演示文稿...")
        presentation_id = create_presentation(service)

        if not presentation_id:
            print("❌ 无法创建演示文稿")
            return

        print(f"\n步骤2: 添加16页内容...")
        print("-" * 70)

        # 添加封面
        add_cover_slide(service, presentation_id, SLIDES_CONTENT[0])

        # 添加其他15页
        for i, content in enumerate(SLIDES_CONTENT[1:], start=2):
            add_content_slide(service, presentation_id, content, i)

        print("\n" + "=" * 70)
      print("✅ 完成！商业计划书已生成")
        print("=" * 70)
        print(f"\n📊 总页数: 16页")
        print(f"\n🔗 Google Slides链接:")
        print(f"https://docs.google.com/presentation/d/{presentation_id}/edit")
        print(f"\n📋 下一步:")
        print("1. 打开链接查看PPT")
      print("2. 在线编辑和优化")
        print("3. 添加图片和图表")
        print("4. 分享给团队成员")
        print("5. 导出为PPTX或PDF")
        print("6. 发送给投资人")
        print()

    except HttpError as error:
        print(f"❌ API调用失败: {error}")
        print("\n可能的原因:")
        print("1. API Key无效")
        print("2. Google Slides API未启用")
        print("3. 配额已用完")
        print("\n请检查Google Cloud Console设置")
if __name__ == "__main__":
    main()
