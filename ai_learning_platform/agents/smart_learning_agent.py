# smart_learning_agent.py
import os
import json
import pickle
import re
from pathlib import Path
from datetime import datetime
import numpy as np
from collections import Counter

from ai_learning_platform.workspace import LearningWorkspace
from ai_learning_platform.workspace.workspace_config import WorkspaceConfig

class SmartLearningAgent:
    """Intelligent agent that maps natural language queries to relevant topics."""
    
    def __init__(self, data_dir=None):
        """Initialize the learning agent with topic hierarchy."""
        self.data_dir = Path(data_dir) if data_dir else Path("learning_data")
        self.data_dir.mkdir(exist_ok=True)
        self.progress_path = self.data_dir / "learning_progress.json"
        self.hierarchy_path = self.data_dir / "topic_hierarchy.pkl"
        self.topic_hierarchy = self._load_topic_hierarchy()
        self.topic_index = self._build_topic_index()
        self.progress = self._load_progress()
        self.project_context = None

    def _load_topic_hierarchy(self):
        """Load the topic hierarchy from file or build from scratch."""
        if self.hierarchy_path.exists():
            with open(self.hierarchy_path, 'rb') as f:
                return pickle.load(f)
        
        # Parse the topic hierarchy text
        hierarchy = {}
        
        # Check if the topic hierarchy file exists
        hierarchy_file = Path("topic_hierarchy.txt")
        if not hierarchy_file.exists():
            print("Warning: topic_hierarchy.txt not found. Creating an empty hierarchy.")
            return {}
        
        with open(hierarchy_file, 'r') as f:
            text = f.read()
        
        # Extract topics with regex
        pattern = r'(\d+(?:\.\d+)*)\s+(.*?)(?=\n\d+(?:\.\d+)*\s+|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for topic_id, topic_name in matches:
            topic_name = topic_name.strip()
            hierarchy[topic_id] = {
                'id': topic_id,
                'name': topic_name,
                'keywords': self._extract_keywords(topic_name),
                'parent': '.'.join(topic_id.split('.')[:-1]) if '.' in topic_id else None,
                'children': []
            }
        
        # Build parent-child relationships
        for topic_id, topic in hierarchy.items():
            parent_id = topic['parent']
            if parent_id and parent_id in hierarchy:
                hierarchy[parent_id]['children'].append(topic_id)
        
        # Save the hierarchy
        with open(self.hierarchy_path, 'wb') as f:
            pickle.dump(hierarchy, f)
            
        return hierarchy
    
    def _extract_keywords(self, topic_name):
        """Extract relevant keywords from topic names."""
        # Remove common words and keep important terms
        common_words = {'and', 'the', 'of', 'for', 'in', 'on', 'by', 'with', 'a', 'an', 'to'}
        return [word.lower() for word in re.findall(r'\b\w+\b', topic_name) 
                if word.lower() not in common_words and len(word) > 2]
    
    def _build_topic_index(self):
        """Build a searchable index of topics with their keywords."""
        index = {}
        
        for topic_id, topic in self.topic_hierarchy.items():
            # Add primary terms from the topic name
            for keyword in topic['keywords']:
                if keyword not in index:
                    index[keyword] = []
                index[keyword].append(topic_id)
            
            # Add the full topic name as a searchable phrase
            name_key = topic['name'].lower()
            if name_key not in index:
                index[name_key] = []
            index[name_key].append(topic_id)
            
            # Add special mapping for common alternative terms
            synonyms = {
                'ml': ['machine learning'],
                'ai': ['artificial intelligence'],
                'ui': ['user interface'],
                'ux': ['user experience'],
                'db': ['database'],
                'os': ['operating system'],
                'web': ['internet', 'website'],
                'crypto': ['cryptography'],
                'malware': ['malicious software', 'virus'],
                'nlp': ['natural language processing'],
                'cnn': ['convolutional neural network'],
                'rnn': ['recurrent neural network']
            }
            
            for keyword in topic['keywords']:
                if keyword in synonyms:
                    for synonym in synonyms[keyword]:
                        if synonym not in index:
                            index[synonym] = []
                        index[synonym].append(topic_id)
        
        return index
    
    def _load_progress(self):
        """Load learning progress from file."""
        if self.progress_path.exists():
            with open(self.progress_path, 'r') as f:
                return json.load(f)
        return {
            'completed_topics': {},
            'in_progress': {},
            'interests': {},  # Using dict instead of Counter for JSON serialization
            'learning_history': [],
            'recommendations': []
        }
    
    def _save_progress(self):
        """Save learning progress to file."""
        with open(self.progress_path, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def load_project_context(self, context_file_path):
        """Load project-specific context."""
        with open(context_file_path, 'r') as f:
            self.project_context = json.load(f)
        
        # Create a project-specific save directory
        project_name = self.project_context['project_name'].lower().replace(' ', '_')
        self.project_dir = self.data_dir / project_name
        self.project_dir.mkdir(exist_ok=True)
        
        # Optionally create a project-specific progress file
        self.project_progress_path = self.project_dir / "project_progress.json"
        
        # Add project keywords to the topic index for better topic matching
        for focus in self.project_context.get('focus_areas', []):
            keywords = self._extract_keywords(focus)
            for keyword in keywords:
                if keyword not in self.topic_index:
                    self.topic_index[keyword] = []
                # Associate with relevant topics based on focus areas
                focus_lower = focus.lower()
                if 'red team' in focus_lower:
                    self.topic_index[keyword].extend(['9.6.4', '9.6.3'])  # Red Team Operations, Social Engineering
                if 'prompt injection' in focus_lower:
                    self.topic_index[keyword].extend(['9.7.4.1', '8.3.6'])  # Attack Techniques against AI, LLMs
                if 'security' in focus_lower:
                    self.topic_index[keyword].extend(['9.1.1', '9.7'])  # Security Fundamentals, AI in Cybersecurity
        
        print(f"Loaded project context for: {self.project_context['project_name']}")
        return self.project_context
    
    def discover_topics(self, query):
        """Discover relevant topics based on a natural language query."""
        query = query.lower()
        relevant_topics = Counter()
        
        # Extract keywords from the query
        query_keywords = [word.lower() for word in re.findall(r'\b\w+\b', query) 
                         if len(word) > 2]
        
        # Find topics matching query keywords
        for keyword in query_keywords:
            if keyword in self.topic_index:
                for topic_id in self.topic_index[keyword]:
                    relevant_topics[topic_id] += 1
        
        # Check for exact topic name matches (stronger signal)
        for phrase, topic_ids in self.topic_index.items():
            if len(phrase.split()) > 1 and phrase in query:
                for topic_id in topic_ids:
                    relevant_topics[topic_id] += 3  # Give higher weight to phrase matches
        
        # Project context boost
        if self.project_context:
            # Boost topics relevant to project focus areas
            for focus_area in self.project_context.get('focus_areas', []):
                focus_keywords = self._extract_keywords(focus_area)
                for keyword in focus_keywords:
                    if keyword in self.topic_index:
                        for topic_id in self.topic_index[keyword]:
                            relevant_topics[topic_id] += 2  # Project context boost
        
        # Get the most relevant topics
        top_topics = relevant_topics.most_common(5)
        
        # If no direct matches, find similar topics
        if not top_topics:
            return self._find_similar_topics(query)
        
        # Include parent topics for context
        contextualized_topics = {}
        for topic_id, count in top_topics:
            if topic_id in self.topic_hierarchy:  # Ensure topic exists in hierarchy
                contextualized_topics[topic_id] = {
                    'relevance': count,
                    'topic': self.topic_hierarchy[topic_id],
                    'context': self._get_topic_context(topic_id)
                }
        
        # Update interest tracking - convert to dict for JSON serialization
        for topic_id, _ in top_topics:
            if topic_id not in self.progress['interests']:
                self.progress['interests'][topic_id] = 0
            self.progress['interests'][topic_id] += 1
            
        self._save_progress()
        
        return contextualized_topics
    
    def _find_similar_topics(self, query):
        """Find topics similar to the query when no direct matches are found."""
        similar_topics = {}
        
        # Find topics with partial keyword matches
        for topic_id, topic in self.topic_hierarchy.items():
            similarity = self._calculate_similarity(query, topic['name'])
            if similarity > 0.4:  # Threshold for similarity
                similar_topics[topic_id] = {
                    'relevance': similarity,
                    'topic': topic,
                    'context': self._get_topic_context(topic_id)
                }
        
        # Return top 5 similar topics
        return dict(sorted(similar_topics.items(), 
                          key=lambda x: x[1]['relevance'], 
                          reverse=True)[:5])
    
    def _calculate_similarity(self, query, topic_name):
        """Calculate simple text similarity between query and topic name."""
        # Simple word overlap for now - could be improved with NLP techniques
        query_words = set(query.lower().split())
        topic_words = set(topic_name.lower().split())
        
        if not query_words or not topic_words:
            return 0
            
        intersection = query_words.intersection(topic_words)
        return len(intersection) / (len(query_words) + len(topic_words) - len(intersection))
    
    def _get_topic_context(self, topic_id):
        """Get the context (ancestors and siblings) for a topic."""
        context = {
            'ancestors': [],
            'siblings': [],
            'children': []
        }
        
        # Get ancestors
        current = topic_id
        while '.' in current:
            parent = '.'.join(current.split('.')[:-1])
            if parent in self.topic_hierarchy:
                context['ancestors'].append({
                    'id': parent,
                    'name': self.topic_hierarchy[parent]['name']
                })
                current = parent
            else:
                break
        
        # Get siblings
        if '.' in topic_id:
            parent = '.'.join(topic_id.split('.')[:-1])
            if parent in self.topic_hierarchy:
                siblings = self.topic_hierarchy[parent].get('children', [])
                context['siblings'] = [
                    {'id': sib, 'name': self.topic_hierarchy[sib]['name']}
                    for sib in siblings if sib != topic_id and sib in self.topic_hierarchy
                ]
        
        # Get children
        children = self.topic_hierarchy[topic_id].get('children', [])
        context['children'] = [
            {'id': child, 'name': self.topic_hierarchy[child]['name']}
            for child in children if child in self.topic_hierarchy
        ]
        
        return context
    
    def learn(self, query):
        """Process a learning query and create personalized learning path."""
        # Discover relevant topics
        discovered_topics = self.discover_topics(query)
        
        if not discovered_topics:
            return {
                "message": "No relevant topics found. Please try a more specific query.",
                "discovered_topics": []
            }
        
        # Create a learning workspace for the top topic
        top_topic_id = list(discovered_topics.keys())[0]
        top_topic = discovered_topics[top_topic_id]['topic']
        
        # Configure workspace for the topic
        workspace_config = self._create_workspace_config(top_topic_id, discovered_topics)
        
        # Create a learning session
        workspace = LearningWorkspace(
            config=workspace_config,
            user_profile=self._create_user_profile(top_topic_id)
        )
        
        # Process the learning query
        augmented_query = self._augment_query(query, top_topic)
        response = workspace.process_learning_session(augmented_query)
        
        # Record the learning session
        self.progress['learning_history'].append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'main_topic': top_topic_id,
            'related_topics': list(discovered_topics.keys())[1:] if len(discovered_topics) > 1 else [],
            'learning_path': response.get('learning_path', [])
        })
        self._save_progress()
        
        # Format the response
        formatted_response = {
            "message": f"Learning path created for: {top_topic['name']}",
            "discovered_topics": [
                {
                    "id": t_id,
                    "name": info['topic']['name'],
                    "relevance": info['relevance']
                } for t_id, info in discovered_topics.items()
            ],
            "learning_path": response.get('learning_path', []),
            "main_topic_context": discovered_topics[top_topic_id]['context']
        }
        
        return formatted_response
    
    def _create_workspace_config(self, topic_id, discovered_topics):
        """Create a workspace configuration for the identified topic."""
        # Extract domains from the topic and its ancestors
        domains = self._extract_domains(topic_id)
        
        # Add domains from related topics
        for related_id in list(discovered_topics.keys())[1:]:
            domains.extend(self._extract_domains(related_id))
        
        # Add project-specific domains if available
        if self.project_context and 'components' in self.project_context:
            for component in self.project_context['components']:
                component_keywords = self._extract_keywords(component.get('name', '') + ' ' + 
                                                         component.get('description', ''))
                for keyword in component_keywords:
                    # Map component keywords to domains
                    if 'manifold' in keyword or 'geometric' in keyword:
                        domains.extend(['differential_geometry', 'topology'])
                    elif 'causal' in keyword:
                        domains.extend(['causal_inference'])
                    elif 'scale' in keyword or 'dynamic' in keyword:
                        domains.extend(['dynamical_systems'])
                    elif 'categor' in keyword:
                        domains.extend(['category_theory'])
                    elif 'security' in keyword or 'attack' in keyword:
                        domains.extend(['security', 'ai_security'])
        
        # Remove duplicates
        domains = list(set(domains))
        
        return WorkspaceConfig(
            domains=domains,
            enable_research=True,
            learning_style="adaptive",
            model_type="advanced",
            tracking_level="detailed"
        )
    
    def _extract_domains(self, topic_id):
        """Extract relevant domains from a topic ID."""
        domains = []
        
        # Map top-level categories to domains
        domain_mappings = {
            "1": ["mathematics", "theory", "foundations"],  # Computing Foundations
            "2": ["hardware", "architecture", "low_level"],  # Hardware Systems
            "3": ["operating_systems", "system", "firmware"],  # System Software
            "4": ["programming", "software_engineering", "coding"],  # Programming
            "5": ["networks", "distributed_systems"],  # Networking
            "6": ["databases", "data_science", "analytics"],  # Data Management
            "7": ["ui", "ux", "design"],  # User Interfaces
            "8": ["ai", "machine_learning", "nlp", "computer_vision"],  # AI
            "9": ["security", "cryptography", "network_security"],  # Cybersecurity
            "10": ["cloud", "edge", "iot", "quantum", "blockchain"],  # Emerging Computing
            "11": ["optimization", "efficiency", "scalability"],  # Performance
            "12": ["ethics", "regulations", "privacy"]  # Legal & Ethical
        }
        
        # Add domains based on top-level category
        if topic_id:
            top_level = topic_id.split('.')[0]
            if top_level in domain_mappings:
                domains.extend(domain_mappings[top_level])
            
            # Add more specific domains for certain subcategories
            if topic_id.startswith('8.2'):  # Machine Learning
                domains.append('machine_learning')
            elif topic_id.startswith('8.3'):  # NLP
                domains.append('natural_language_processing')
            elif topic_id.startswith('8.4'):  # Computer Vision
                domains.append('computer_vision')
            elif topic_id.startswith('9.2'):  # Cryptography
                domains.append('cryptography')
            elif topic_id.startswith('9.7'):  # AI in Cybersecurity
                domains.extend(['ai_security', 'threat_detection'])
        
        return domains
    
    def _create_user_profile(self, topic_id):
        """Create a user profile for the learning workspace."""
        # Get completed and in-progress topics
        completed_topics = list(self.progress['completed_topics'].keys())
        in_progress = list(self.progress['in_progress'].keys())
        
        # Add project context if available
        project_info = {}
        if self.project_context:
            project_info = {
                "project_name": self.project_context['project_name'],
                "focus_areas": self.project_context.get('focus_areas', []),
                "hardware": self.project_context.get('hardware', []),
                "objective": self.project_context.get('objective', '')
            }
        
        # Create profile with learning history
        profile = {
            "topic_id": topic_id,
            "topic_name": self.topic_hierarchy.get(topic_id, {}).get('name', 'Unknown Topic'),
            "completed_topics": completed_topics,
            "in_progress_topics": in_progress,
            "interests": [t for t in self.progress['interests'].keys()],
            "learning_style": "adaptive"
        }
        
        # Merge project info if available
        if project_info:
            profile.update(project_info)
            
        return profile
    
    def _augment_query(self, query, topic):
        """Augment the query with topic-specific and project context."""
        # Add topic context to the query
        topic_context = f"I want to learn about {topic['name']}. "
        
        # Add project context if available
        project_context = ""
        if hasattr(self, 'project_context') and self.project_context:
            project = self.project_context
            project_context = f"I'm working on {project['project_name']}, which is "
            if 'project_description' in project:
                project_context += f"{project['project_description']}. "
            elif 'objective' in project:
                project_context += f"focused on {project['objective']}. "
            else:
                project_context += "a specialized project. "
                
            if 'focus_areas' in project and project['focus_areas']:
                project_context += f"I'm specifically interested in {', '.join(project['focus_areas'])}. "
        
        # Add information about completed topics if relevant
        completed_info = ""
        ancestors = []
        current = topic['id']
        while '.' in current:
            parent = '.'.join(current.split('.')[:-1])
            if parent in self.topic_hierarchy:
                ancestors.append(parent)
                current = parent
            else:
                break
        
        completed_ancestors = [a for a in ancestors if a in self.progress['completed_topics']]
        if completed_ancestors:
            completed_names = [self.topic_hierarchy[a]['name'] for a in completed_ancestors]
            completed_info = f"I've already learned about {', '.join(completed_names)}. "
        
        return f"{topic_context}{project_context}{completed_info}{query}"
    
    def update_progress(self, topic_query, status="completed"):
        """Update learning progress for a topic (using natural language)."""
        # Find the topic
        topic_id = self._find_topic_by_name(topic_query)
        
        if not topic_id:
            return {
                "message": f"Topic '{topic_query}' not found. Please provide a more specific topic name.",
                "success": False
            }
        
        # Update progress based on status
        if status == "completed":
            self.progress['completed_topics'][topic_id] = {
                "completed_date": datetime.now().isoformat(),
                "topic_name": self.topic_hierarchy[topic_id]['name']
            }
            # Remove from in_progress if present
            if topic_id in self.progress['in_progress']:
                del self.progress['in_progress'][topic_id]
        elif status == "in_progress":
            self.progress['in_progress'][topic_id] = {
                "start_date": datetime.now().isoformat(),
                "topic_name": self.topic_hierarchy[topic_id]['name']
            }
        elif status == "reset":
            # Remove from both completed and in_progress
            if topic_id in self.progress['completed_topics']:
                del self.progress['completed_topics'][topic_id]
            if topic_id in self.progress['in_progress']:
                del self.progress['in_progress'][topic_id]
        
        self._save_progress()
        
        return {
            "message": f"Progress updated for: {self.topic_hierarchy[topic_id]['name']}",
            "status": status,
            "topic_id": topic_id,
            "topic_name": self.topic_hierarchy[topic_id]['name'],
            "success": True
        }
    
    def _find_topic_by_name(self, topic_query):
        """Find a topic ID by name or keywords."""
        topic_query = topic_query.lower()
        
        # Check for exact name match
        for topic_id, topic in self.topic_hierarchy.items():
            if topic['name'].lower() == topic_query:
                return topic_id
        
        # Check for partial name match
        for topic_id, topic in self.topic_hierarchy.items():
            if topic_query in topic['name'].lower():
                return topic_id
        
        # Check for keyword match
        relevant_topics = Counter()
        query_keywords = [word.lower() for word in re.findall(r'\b\w+\b', topic_query) 
                         if len(word) > 2]
        
        for keyword in query_keywords:
            if keyword in self.topic_index:
                for topic_id in self.topic_index[keyword]:
                    relevant_topics[topic_id] += 1
        
        if relevant_topics:
            return relevant_topics.most_common(1)[0][0]
        
        return None
    
    def get_recommendations(self):
        """Get personalized learning recommendations based on progress and interests."""
        recommendations = []
        
        # Calculate completion percentage for each top-level category
        category_completion = {}
        for i in range(1, 13):  # 12 top-level categories
            category = str(i)
            total_topics = 0
            completed_topics = 0
            
            for topic_id in self.topic_hierarchy:
                if topic_id.startswith(category + '.'):
                    total_topics += 1
                    if topic_id in self.progress['completed_topics']:
                        completed_topics += 1
            
            if total_topics > 0:
                completion_pct = (completed_topics / total_topics) * 100
                category_completion[category] = {
                    'percentage': completion_pct,
                    'completed': completed_topics,
                    'total': total_topics,
                    'name': self.topic_hierarchy[category]['name'] if category in self.topic_hierarchy else f"Category {category}"
                }
        
        # 1. Recommend next topics in partially completed categories
        partial_categories = [c for c, info in category_completion.items() 
                            if 10 <= info['percentage'] < 80]
        
        for category in partial_categories[:2]:  # Top 2 partial categories
            next_topics = self._find_next_topics_in_category(category)
            if next_topics:
                recommendations.append({
                    'type': 'continue_category',
                    'category_name': category_completion[category]['name'],
                    'completion': category_completion[category]['percentage'],
                    'topics': next_topics[:3]  # Top 3 recommended topics
                })
        
        # 2. Project-related recommendations
        if hasattr(self, 'project_context') and self.project_context:
            project_topics = self._find_project_related_topics()
            if project_topics:
                recommendations.append({
                    'type': 'project_related',
                    'message': f"These topics are relevant to your {self.project_context['project_name']} project:",
                    'topics': project_topics[:3]
                })
        
        # 3. Recommend related topics to completed ones
        completed_ids = list(self.progress['completed_topics'].keys())
        if completed_ids:
            related_topics = self._find_related_topics(completed_ids[-5:])  # Based on last 5 completed
            if related_topics:
                recommendations.append({
                    'type': 'related_topics',
                    'based_on': [self.topic_hierarchy[t]['name'] for t in completed_ids[-3:]],
                    'topics': related_topics[:3]  # Top 3 related topics
                })
        
        # 4. Recommend based on interests
        if self.progress['interests']:
            interest_topics = []
            for topic_id in list(self.progress['interests'].keys())[:5]:  # Top 5 interests
                if topic_id in self.topic_hierarchy:
                    # Find subtopics not yet completed
                    for potential_subtopic_id, topic in self.topic_hierarchy.items():
                        if (potential_subtopic_id.startswith(topic_id + '.') and 
                            potential_subtopic_id not in self.progress['completed_topics']):
                            interest_topics.append({
                                'id': potential_subtopic_id,
                                'name': topic['name'],
                                'parent': topic_id
                            })
            
            if interest_topics:
                recommendations.append({
                    'type': 'interest_based',
                    'topics': interest_topics[:3]  # Top 3 interest topics
                })
        
        # 5. Recommend foundational topics if beginner
        if len(self.progress['completed_topics']) < 10:
            foundational_topics = self._get_foundational_topics()
            if foundational_topics:
                recommendations.append({
                    'type': 'foundational',
                    'message': "These foundational topics will help you build a strong base:",
                    'topics': foundational_topics[:3]  # Top 3 foundational topics
                })
        
        # Save recommendations
        self.progress['recommendations'] = recommendations
        self._save_progress()
        
        return recommendations
    
    def _find_project_related_topics(self):
        """Find topics especially relevant to the current project."""
        if not hasattr(self, 'project_context') or not self.project_context:
            return []
            
        project_topics = []
        
        # Get keywords from focus areas and components
        keywords = []
        for focus in self.project_context.get('focus_areas', []):
            keywords.extend(self._extract_keywords(focus))
            
        for component in self.project_context.get('components', []):
            keywords.extend(self._extract_keywords(component.get('name', '')))
            keywords.extend(self._extract_keywords(component.get('description', '')))
            
        # Remove duplicates
        keywords = list(set(keywords))
        
        # Find matching topics not yet completed
        for keyword in keywords:
            if keyword in self.topic_index:
                for topic_id in self.topic_index[keyword]:
                    if (topic_id not in self.progress['completed_topics'] and
                        topic_id not in [t['id'] for t in project_topics] and
                        topic_id in self.topic_hierarchy):
                        project_topics.append({
                            'id': topic_id,
                            'name': self.topic_hierarchy[topic_id]['name'],
                            'keyword': keyword
                        })
        
        return project_topics
    
    def _find_next_topics_in_category(self, category):
        """Find recommended next topics in a category based on progress."""
        next_topics = []
        
        # Find completed topics in this category
        completed_in_category = [t for t in self.progress['completed_topics'] 
                               if t.startswith(category + '.')]
        
        # Find topics that build on completed ones (next in sequence)
        for completed in completed_in_category:
            # Look for topics with one more level
            parts = completed.split('.')
            if len(parts) < 4:  # Don't go too deep
                parent_prefix = completed + '.'
                for topic_id, topic in self.topic_hierarchy.items():
                    if (topic_id.startswith(parent_prefix) and 
                        topic_id not in self.progress['completed_topics']):
                        next_topics.append({
                            'id': topic_id,
                            'name': topic['name'],
                            'builds_on': completed
                        })
        
        # If no topics build directly on completed ones, suggest siblings
        if not next_topics:
            for completed in completed_in_category:
                if '.' in completed:
                    parent = '.'.join(completed.split('.')[:-1])
                    for topic_id, topic in self.topic_hierarchy.items():
                        if (topic_id.startswith(parent + '.') and 
                            topic_id != completed and
                            topic_id not in self.progress['completed_topics']):
                            next_topics.append({
                                'id': topic_id,
                                'name': topic['name'],
                                'relationship': 'sibling'
                            })
        
        return next_topics
    
    def _find_related_topics(self, completed_ids):
        """Find topics related to recently completed ones."""
        related_topics = []
        
        for completed_id in completed_ids:
            if completed_id in self.topic_hierarchy:
                topic_name = self.topic_hierarchy[completed_id]['name']
                keywords = self._extract_keywords(topic_name)
                
                # Find topics with similar keywords
                for topic_id, topic in self.topic_hierarchy.items():
                    if (topic_id not in self.progress['completed_topics'] and
                        topic_id not in [t['id'] for t in related_topics]):
                        
                        topic_keywords = self._extract_keywords(topic['name'])
                        common_keywords = set(keywords).intersection(set(topic_keywords))
                        
                        if common_keywords and not self._is_ancestor_or_descendant(completed_id, topic_id):
                            related_topics.append({
                                'id': topic_id,
                                'name': topic['name'],
                                'common_keywords': list(common_keywords),
                                'related_to': completed_id
                            })
        
        # Sort by number of common keywords
        return sorted(related_topics, 
                     key=lambda x: len(x.get('common_keywords', [])), 
                     reverse=True)
    
    def _is_ancestor_or_descendant(self, topic1, topic2):
        """Check if one topic is an ancestor or descendant of another."""
        return topic1.startswith(topic2) or topic2.startswith(topic1)
    
    def _get_foundational_topics(self):
        """Get fundamental topics for beginners."""
        foundational_topics = []
        
        # Define key foundational topic IDs
        foundation_ids = [
            '1.1.1',  # Discrete Mathematics
            '1.2.3',  # Algorithm Design and Analysis
            '2.1.1',  # CPU Design and Operation
            '3.2.1',  # OS Fundamentals
            '4.1.1',  # Imperative Programming
            '5.1.1',  # Network Fundamentals
            '9.1.1'   # Security Fundamentals
        ]
        
        for topic_id in foundation_ids:
            if topic_id in self.topic_hierarchy and topic_id not in self.progress['completed_topics']:
                foundational_topics.append({
                    'id': topic_id,
                    'name': self.topic_hierarchy[topic_id]['name'],
                    'type': 'foundational'
                })
        
        return foundational_topics
    
    def get_learning_progress(self):
        """Get a summary of learning progress."""
        # Count completed topics per category
        category_stats = {}
        for topic_id in self.progress['completed_topics']:
            if topic_id in self.topic_hierarchy:
                category = topic_id.split('.')[0]
                if category not in category_stats:
                    category_stats[category] = {
                        'completed': 0,
                        'name': self.topic_hierarchy[category]['name'] if category in self.topic_hierarchy else f"Category {category}"
                    }
                category_stats[category]['completed'] += 1
        
        # Count total topics per category
        for topic_id in self.topic_hierarchy:
            if '.' in topic_id:  # Skip top-level categories
                category = topic_id.split('.')[0]
                if category in category_stats:
                    if 'total' not in category_stats[category]:
                        category_stats[category]['total'] = 0
                    category_stats[category]['total'] += 1
        
        # Calculate percentages
        for category, stats in category_stats.items():
            if 'total' in stats and stats['total'] > 0:
                stats['percentage'] = (stats['completed'] / stats['total']) * 100
            else:
                stats['percentage'] = 0
        
        # Get recently completed topics
        recent_completed = [
            {
                'id': topic_id,
                'name': self.topic_hierarchy[topic_id]['name'],
                'completed_date': info['completed_date']
            }
            for topic_id, info in self.progress['completed_topics'].items()
            if topic_id in self.topic_hierarchy
        ]
        recent_completed.sort(key=lambda x: x['completed_date'], reverse=True)
        
        # Get in-progress topics
        in_progress = [
            {
                'id': topic_id,
                'name': self.topic_hierarchy[topic_id]['name'],
                'start_date': info['start_date']
            }
            for topic_id, info in self.progress['in_progress'].items()
            if topic_id in self.topic_hierarchy
        ]
        
        return {
            'category_stats': category_stats,
            'total_completed': len(self.progress['completed_topics']),
            'total_in_progress': len(self.progress['in_progress']),
            'recent_completed': recent_completed[:5],  # Last 5 completed
            'in_progress': in_progress,
            'recommendations': self.get_recommendations()
        }