import click
import os
from src.core.loader import ConfigLoader
from src.core.engine import SyncEngine

@click.command()
@click.option('--config', '-c', required=True, help='YAML配置文件路径')
@click.option('--output', '-o', default='./output', help='输出目录路径')
def main(config, output):
    """Doris同步自动化工具 - MVP版本
    
    从MySQL自动采集元数据，生成Doris建表SQL和DataX同步配置
    """
    
    # 加载并验证配置
    click.echo(f"正在加载配置文件：{config}")
    config_data = ConfigLoader.load(config)
    ConfigLoader.validate(config_data)
    
    # 获取模板目录
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'templates')
    if not os.path.exists(template_dir):
        # 尝试从当前工作目录查找
        template_dir = os.path.join(os.getcwd(), 'config', 'templates')
    
    if not os.path.exists(template_dir):
        click.echo(f"❌ 模板目录不存在：{template_dir}")
        return
    
    # 执行引擎
    engine = SyncEngine(config_data, template_dir)
    engine.execute(output)

if __name__ == '__main__':
    main()
