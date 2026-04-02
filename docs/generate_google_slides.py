"
Nautilus Pitch Deck Generator - Google Slides版本
直接生成Google Slides在线PPT

依赖:
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
使用方法:
1. 确保已启用Google Slides API
2. 提供API凭证（API Key或OAuth）
3. 运行: python generate_google_slides.py
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

# API配置
GOOGLE_API_KEY = "AIzaSyAbLcIXvJiAzKJ-ntW6Jmcd8KcW_LPkz0Y"

# 配色方案（RGB 0-1范围）
COLORS = {
    'primary_blue': {'red': 0, 'green': 0.4, 'blue': 1},
    'dark_blue': {'red': 0, 'green': 0.2, 'blue': 0.4},
    'gold': {'red': 1, 'green': 0.72, 'blue': 0},
    'white': {'red': 1, 'green': 1, 'blue': 1},
    'dark_gray': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
}

def create_presentation(service):
    ""创建新的演示文稿"""
    try:
        presentation = {
            'title': 'Nautilus - AI Agent价值互联网平台'
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

def add_slide_with_title(service, presentation_id, title_text, page_number):
    """添加带标题的幻灯片"""
    requests = [
        {
            'createSlide': {
                'slideLayoutReference': {
          'predefinedLayout': 'BLANK'
           }
       }
        }
    ]

    try:
      # 创建幻灯片
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

        slide_id = response.get('replies')[0].get('createSlide').get('objectId')

        # 添加标题
      requests = [
            {
                'createShape': {
                    'objectId': f'title_{page_number}',
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                   'pageObjectId': slide_id,
            'size': {
          'width': {'magnitude': 720, 'unit': 'PT'},
                      'height': {'magnitude': 60, 'unit': 'PT'}
                        },
         'transform': {
                  'scaleX': 1,
             'scaleY': 1,
                'translateX': 36,
                      'translateY': 36,
                    'unit': 'PT'
                }
              }
            }
            },
            {
                'insertText': {
                 'objectId': f'title_{page_number}',
                    'text': title_text
                }
          },
            {
                'updateTextStyle': {
                    'objectId': f'title_{page_number}',
              'style': {
                        'fontSize': {
                'magnitude': 44,
              'unit': 'PT'
                },
                 'bold': True,
                 'foregroundColor': {
                  'opaqueColor': {
                   'rgbColor': COLORS['dark_blue']
           }
            }
                  },
            'fields': 'fontSize,bold,foregroundColor'
         }
            }
        ]

        service.presentations().batchUpdate(
          presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

      print(f'✅ 第{page_number}页已添加: {title_text}')
        return slide_id

    except HttpError as error:
        print(f'❌ 添加幻灯片失败: {error}')
        return None

def create_cover_slide(service, presentation_id):
    """创建封面"""
    requests = [
        {
            'createSlide': {
                'slideLayoutReference': {
                'predefinedLayout': 'BLANK'
            }
            }
        }
    ]

    try:
        response = service.presentations().batchUpdate(
        presentationId=presentation_id,
          body={'requests': requests}
        ).execute()

        slide_id = response.get('replies')[0].get('createSlide').get('objectId')

        # 添加背景色
        requests = [
        {
          'updatePageProperties': {
              'objectId': slide_id,
                    'pageProperties': {
                   'pageBackgroundFill': {
                  'solidFill': {
               'color': {
                             'rgbColor': COLORS['dark_blue']
                          }
                       }
            }
                    },
            'fields': 'pageBackgroundFill'
             }
            }
        ]

        # 添加标题 "Nautilus"
        requests.append({
      'createShape': {
             'objectId': 'cover_title',
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                  'pageObjectId': slide_id,
                  'size': {
                     'width': {'magnitude': 600, 'unit': 'PT'},
                   'height': {'magnitude': 100, 'unit': 'PT'}
          },
               'transform': {
                 'scaleX': 1,
                'scaleY': 1,
                 'translateX': 180,
                      'translateY': 200,
                'unit': 'PT'
                    }
                }
          }
     })

        requests.append({
            'insertText': {
                'objectId': 'cover_title',
                'text': 'Nautilus'
            }
        })

        requests.append({
          'updateTextStyle': {
          'objectId': 'cover_title',
       'style': {
               'fontSize': {'magnitude': 72, 'unit': 'PT'},
                 'bold': True,
             'foregroundColor': {
          'opaqueColor': {'rgbColor': COLORS['white']}
                    }
        },
             'fields': 'fontSize,bold,foregroundColor'
            }
        })

        requests.append({
            'updateParagraphStyle': {
                'objectId': 'cover_title',
                'style': {
                    'alignment': 'CENTER'
              },
                'fields': 'alignment'
            }
        })

        # 添加副标题
        requests.append({
      'createShape': {
                'objectId': 'cover_subtitle',
            'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                  'width': {'magnitude': 600, 'unit': 'PT'},
                'height': {'magnitude': 60, 'unit': 'PT'}
              },
                    'transform': {
            'scaleX': 1,
            'scaleY': 1,
               'translateX': 180,
             'translateY': 320,
              'unit': 'PT'
             }
                }
         }
      })

      requests.append({
            'insertText': {
                'objectId': 'cover_subtitle',
           'text': 'AI Agent价值互联网平台'
            }
        })

     requests.append({
          'updateTextStyle': {
            'objectId': 'cover_subtitle',
                'style': {
                 'fontSize': {'magnitude': 36, 'unit': 'PT'},
                    'foregroundColor': {
                  'opaqueColor': {'rgbColor': COLORS['gold']}
        }
                },
                'fields': 'fontSize,foregroundColor'
            }
        })

        requests.append({
         'updateParagraphStyle': {
                'objectId': 'cover_subtitle',
                'style': {
                  'alignment': 'CENTER'
              },
        'fields': 'alignment'
            }
        })

        # 添加标语
        requests.append({
            'createShape': {
                'objectId': 'cover_tagline',
             'shapeType': 'TEXT_BOX',
           'elementProperties': {
                  'pageObjectId': slide_id,
                    'size': {
           'width': {'magnitude': 600, 'unit': 'PT'},
          'height': {'magnitude': 40, 'unit': 'PT'}
          },
                    'transform': {
                'scaleX': 1,
         'scaleY': 1,
                        'translateX': 180,
              'translateY': 390,
                 'unit': 'PT'
         }
                }
            }
        })

        requests.append({
            'insertText': {
       'objectId': 'cover_tagline',
        'text': '两篇顶级论文的延伸与精彩呈现'
            }
        })

        requests.append({
            'updateTextStyle': {
          'objectId': 'cover_tagline',
                'style': {
         'fontSize': {'magnitude': 24, 'unit': 'PT'},
                    'foregroundColor': {
                   'opaqueColor': {'rgbColor': COLORS['white']}
             }
                },
          'fields': 'fontSize,foregroundColor'
         }
        })

        requests.append({
            'updateParagraphStyle': {
                'objectId': 'cover_tagline',
                'style': {
               'alignment': 'CENTER'
          },
                'fields': 'alignment'
            }
      })

        # 添加融资信息
        requests.append({
            'createShape': {
                'objectId': 'cover_funding',
                'shapeType': 'TEXT_BOX',
         'elementProperties': {
           'pageObjectId': slide_id,
                    'size': {
             'width': {'magnitude': 600, 'unit': 'PT'},
              'height': {'magnitude': 40, 'unit': 'PT'}
           },
          'transform': {
                  'scaleX': 1,
                   'scaleY': 1,
                        'translateX': 180,
               'translateY': 460,
              'unit': 'PT'
                    }
          }
            }
        })

        requests.append({
            'insertText': {
                'objectId': 'cover_funding',
             'text': '种子轮融资 | $2M-$5M'
            }
        })

        requests.append({
         'updateTextStyle': {
                'objectId': 'cover_funding',
                'style': {
              'fontSize': {'magnitude': 20, 'unit': 'PT'},
                    'foregroundColor': {
                'opaqueColor': {'rgbColor': COLORS['gold']}
             }
                },
                'fields': 'fontSize,foregroundColor'
            }
        })

     requests.append({
            'updateParagraphStyle': {
            'objectId': 'cover_funding',
                'style': {
          'alignment': 'CENTER'
             },
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

def main():
    """主函数"""
    print("=" * 60)
    print("Nautilus Google Slides Generator")
    print("=" * 60)
    print()

    try:
        # 使用API Key创建服务
        service = build('slides', 'v1', developerKey=GOOGLE_API_KEY)

        print("步骤1: 创建演示文稿...")
        presentation_id = create_presentation(service)

        if not presentation_id:
      print("❌ 无法创建演示文稿")
         return

        print("\n步骤2: 创建封面...")
        create_cover_slide(service, presentation_id)

        print("\n步骤3: 添加其他页面...")
      slides_titles = [
            "AI Agent市场的四大痛点",
        "Nautilus = Epiplexity + DMAS",
       "基于两篇顶级AI研究论文",
            "$950B市场机会",
            "Trinity Engine - 三层架构",
          "多元化收入模式",
            "五大核心优势",
            "已完成的里程碑",
            "3年增长计划",
            "三阶段增长策略",
         "经验丰富的核心团队",
            "融资$2M-$5M",
            "成为Agent价值互联网基础设施",
          "让我们一起改变AI的未来"
        ]

        for i, title in enumerate(slides_titles, start=2):
            add_slide_with_title(service, presentation_id, title, i)

        print("\n" + "=" * 60)
        print("✅ 完成！")
        print("=" * 60)
        print(f"\nGoogle Slides链接:")
        print(f"https://docs.google.com/presentation/d/{presentation_id}/edit")
     print("\n下一步:")
        print("1. 打开链接查看PPT")
        print("2. 在线编辑和优化")
        print("3. 添加图片和图表")
     print("4. 分享给团队成员")
        print("5. 导出为PPTX或PDF")
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
