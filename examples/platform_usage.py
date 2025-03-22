import asyncio
import os
import logging
from dotenv import load_dotenv
from ai_learning_platform.startup import PlatformInitializer
from ai_learning_platform.learning.session_manager import LearningSession
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

logger = logging.getLogger(__name__)
console = Console()

async def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize platform with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[green]Initializing AI Learning Platform...", total=100)
            
            logger.info("Initializing AI Learning Platform...")
            initializer = PlatformInitializer()
            platform_components = await initializer.initialize()
            
            # Create the learning session using the components from the dictionary
            session = LearningSession(
                model_handler=platform_components['model_handler'],
                knowledge_graph=platform_components['knowledge_graph'],
                progress_tracker=platform_components['progress_tracker']
            )
            progress.update(task, completed=100)

        while True:
            # Get user input
            query = Prompt.ask(
                "\n[bold cyan]What would you like to learn about? (or type 'exit' to quit)[/bold cyan]"
            )
            
            if query.lower() == 'exit':
                break

            # Process query with status spinner
            with console.status("[bold green]Analyzing your learning needs...", spinner="dots"):
                logger.info("Processing learning query...")
                response = await session.process_query(query)

            # Handle the response
            if response and isinstance(response, dict):
                if 'learning_path' in response:
                    for step in response['learning_path']:
                        console.print(Panel(
                            f"[bold]{step['topic_id']}[/bold]\n\n"
                            f"{step['metadata']['description']}\n\n"
                            f"[bold]Prerequisites:[/bold] {', '.join(step['metadata']['prerequisites'])}\n"
                            f"[bold]Key Concepts:[/bold]\n" + 
                            "\n".join(f"• {concept}" for concept in step['metadata']['key_concepts']),
                            title="Learning Module",
                            border_style="blue"
                        ))

                        if Confirm.ask("\nWould you like more details about this topic?"):
                            detailed_response = await session.process_query(
                                f"Please explain {step['topic_id']} in detail, including code examples and best practices"
                            )
                            console.print(Panel(
                                Markdown(detailed_response.get('content', 'No detailed information available')),
                                title="Detailed Information",
                                border_style="green"
                            ))

                        if Confirm.ask("\nWould you like to see some practical exercises?"):
                            exercises = await session.process_query(
                                f"Give me some hands-on exercises for {step['topic_id']}"
                            )
                            console.print(Panel(
                                Markdown(exercises.get('content', 'No exercises available')),
                                title="Practical Exercises",
                                border_style="yellow"
                            ))
                elif 'content' in response:
                    # Direct response without learning path
                    console.print(Panel(
                        Markdown(response['content']),
                        title="Response",
                        border_style="blue"
                    ))
                else:
                    console.print("[red]Failed to generate a response. Please try again.[/red]")
            else:
                console.print("[red]Failed to generate a response. Please try again.[/red]")

            # Ask if user wants to continue
            if not Confirm.ask("\nWould you like to explore another topic?"):
                break

        console.print("\n[bold green]Thank you for using the AI Learning Platform![/bold green]")

    except Exception as e:
        logger.error(f"Error during learning session: {str(e)}", exc_info=True)
        console.print(f"\n[red]Error:[/red] {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
