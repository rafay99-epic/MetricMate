import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
import os
from pathlib import Path
import time
from tkcalendar import DateEntry
import json
from scipy import stats

# Tokyo Night color scheme
TOKYO_NIGHT = {
    'bg': '#1a1b26',
    'fg': '#a9b1d6',
    'accent': '#7aa2f7',
    'secondary': '#bb9af7',
    'success': '#9ece6a',
    'warning': '#e0af68',
    'error': '#f7768e',
    'graph_bg': '#24283b',
    'graph_grid': '#414868',
    'graph_line': '#7aa2f7',
    'graph_text': '#c0caf5'
}

class GamingAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gaming Performance Analyzer")
        
        # Set minimum window size
        self.root.minsize(800, 600)
        
        # Make the window resizable
        self.root.resizable(True, True)
        
        # Initialize variables
        self.df = None
        self.current_graph = None
        self.analysis_text = None
        self.last_draw_time = 0
        self.draw_throttle = 100  # milliseconds between redraws
        self.alert_thresholds = {
            'temperature': 80,  # °C
            'cpu_usage': 90,    # %
            'gpu_usage': 90     # %
        }
        
        # Configure theme colors
        self.configure_theme()
        
        # Configure matplotlib style
        self.configure_matplotlib()
        
        self.create_widgets()
        
        # Configure grid weights for main window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def configure_theme(self):
        """Configure the Tokyo Night theme"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.root.configure(bg=TOKYO_NIGHT['bg'])
        
        # Configure ttk styles
        self.style.configure('TFrame', background=TOKYO_NIGHT['bg'])
        self.style.configure('TLabel', background=TOKYO_NIGHT['bg'], foreground=TOKYO_NIGHT['fg'])
        self.style.configure('TButton', 
                           background=TOKYO_NIGHT['accent'],
                           foreground=TOKYO_NIGHT['bg'],
                           padding=5)
        self.style.configure('TLabelframe', 
                           background=TOKYO_NIGHT['bg'],
                           foreground=TOKYO_NIGHT['fg'])
        self.style.configure('TLabelframe.Label', 
                           background=TOKYO_NIGHT['bg'],
                           foreground=TOKYO_NIGHT['fg'])
        self.style.configure('TCombobox',
                           fieldbackground=TOKYO_NIGHT['graph_bg'],
                           background=TOKYO_NIGHT['accent'],
                           foreground=TOKYO_NIGHT['fg'],
                           arrowcolor=TOKYO_NIGHT['fg'])
        
    def configure_matplotlib(self):
        """Configure matplotlib with Tokyo Night theme"""
        plt.style.use('dark_background')
        plt.rcParams.update({
            'figure.facecolor': TOKYO_NIGHT['graph_bg'],
            'axes.facecolor': TOKYO_NIGHT['graph_bg'],
            'axes.edgecolor': TOKYO_NIGHT['graph_grid'],
            'axes.labelcolor': TOKYO_NIGHT['graph_text'],
            'axes.grid': True,
            'grid.color': TOKYO_NIGHT['graph_grid'],
            'grid.linestyle': '--',
            'grid.alpha': 0.3,
            'text.color': TOKYO_NIGHT['graph_text'],
            'xtick.color': TOKYO_NIGHT['graph_text'],
            'ytick.color': TOKYO_NIGHT['graph_text'],
            'figure.titlesize': 12,
            'axes.titlesize': 11,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.facecolor': TOKYO_NIGHT['graph_bg'],
            'legend.edgecolor': TOKYO_NIGHT['graph_grid'],
            'legend.labelcolor': TOKYO_NIGHT['graph_text']
        })
        
    def create_widgets(self):
        # Create main container with padding
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for main container
        self.main_container.grid_rowconfigure(1, weight=1)  # Graph section
        self.main_container.grid_rowconfigure(2, weight=1)  # Text section
        self.main_container.grid_columnconfigure(1, weight=3)  # Graph section
        self.main_container.grid_columnconfigure(0, weight=1)  # Controls section
        
        # Create menu bar
        self.create_menu()
        
        # File selection section
        self.create_file_section()
        
        # Analysis options section
        self.create_analysis_section()
        
        # Graph display section
        self.create_graph_section()
        
        # Analysis text section
        self.create_text_section()
        
    def create_menu(self):
        """Create the menu bar with additional features"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load CSV", command=self.load_csv)
        file_menu.add_command(label="Export Analysis", command=self.export_analysis)
        file_menu.add_command(label="Export Graph", command=self.save_graph)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Statistical Analysis", command=self.show_statistical_analysis)
        analysis_menu.add_command(label="Performance Trends", command=self.show_performance_trends)
        analysis_menu.add_command(label="Anomaly Detection", command=self.detect_anomalies)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Alert Thresholds", command=self.configure_alerts)
        settings_menu.add_command(label="Graph Settings", command=self.configure_graph_settings)
        
    def create_file_section(self):
        file_frame = ttk.LabelFrame(self.main_container, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights for file frame
        file_frame.grid_columnconfigure(1, weight=1)
        
        # Style the button
        select_button = ttk.Button(file_frame, text="Select CSV File", command=self.load_csv)
        select_button.grid(row=0, column=0, padx=5)
        
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
    def create_analysis_section(self):
        analysis_frame = ttk.LabelFrame(self.main_container, text="Analysis Options", padding="10")
        analysis_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights for analysis frame
        analysis_frame.grid_columnconfigure(1, weight=1)
        
        # Graph type selection
        ttk.Label(analysis_frame, text="Graph Type:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.graph_type = ttk.Combobox(analysis_frame, values=[
            "Temperature", "CPU Usage", "GPU Usage", "All Metrics",
            "Correlation", "Heatmap", "Performance Trends"
        ])
        self.graph_type.grid(row=0, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.graph_type.set("Temperature")
        
        # Time range selection
        ttk.Label(analysis_frame, text="Time Range:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.time_range = ttk.Combobox(analysis_frame, values=[
            "All", "Morning (6AM-12PM)", "Afternoon (12PM-6PM)", 
            "Evening (6PM-12AM)", "Night (12AM-6AM)", "Custom Range"
        ])
        self.time_range.grid(row=1, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.time_range.set("All")
        self.time_range.bind('<<ComboboxSelected>>', self.on_time_range_change)
        
        # Custom date range frame
        self.date_frame = ttk.Frame(analysis_frame)
        self.date_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.date_frame, text="From:").grid(row=0, column=0, padx=5)
        self.start_date = DateEntry(self.date_frame, width=12, background=TOKYO_NIGHT['accent'],
                                  foreground=TOKYO_NIGHT['bg'], borderwidth=2)
        self.start_date.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.date_frame, text="To:").grid(row=0, column=2, padx=5)
        self.end_date = DateEntry(self.date_frame, width=12, background=TOKYO_NIGHT['accent'],
                                foreground=TOKYO_NIGHT['bg'], borderwidth=2)
        self.end_date.grid(row=0, column=3, padx=5)
        
        self.date_frame.grid_remove()  # Hide initially
        
        # Analysis button
        analyze_button = ttk.Button(analysis_frame, text="Analyze", command=self.analyze_data)
        analyze_button.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
    def on_time_range_change(self, event):
        """Handle time range selection change"""
        if self.time_range.get() == "Custom Range":
            self.date_frame.grid()
        else:
            self.date_frame.grid_remove()
            
    def create_graph_section(self):
        graph_frame = ttk.LabelFrame(self.main_container, text="Graph Display", padding="10")
        graph_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights for graph frame
        graph_frame.grid_rowconfigure(0, weight=1)
        graph_frame.grid_columnconfigure(0, weight=1)
        
        # Create a canvas with scrollbars
        canvas_frame = ttk.Frame(graph_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for canvas frame
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas with double buffering
        self.graph_canvas = tk.Canvas(canvas_frame, bg=TOKYO_NIGHT['graph_bg'], highlightthickness=0)
        self.graph_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.graph_canvas.yview)
        y_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        x_scrollbar = ttk.Scrollbar(graph_frame, orient=tk.HORIZONTAL, command=self.graph_canvas.xview)
        x_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure canvas
        self.graph_canvas.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Create frame for matplotlib figure
        self.fig_frame = ttk.Frame(self.graph_canvas)
        self.graph_canvas.create_window((0, 0), window=self.fig_frame, anchor=tk.NW)
        
        # Create figure for matplotlib with optimized settings
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.fig_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar with custom styling
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.fig_frame)
        self.toolbar.update()
        
        # Configure scroll region with throttling
        def configure_scroll_region(event):
            current_time = int(time.time() * 1000)
            if current_time - self.last_draw_time > self.draw_throttle:
                self.graph_canvas.configure(scrollregion=self.graph_canvas.bbox("all"))
                self.last_draw_time = current_time
        
        self.fig_frame.bind("<Configure>", configure_scroll_region)
        
        # Add mouse wheel scrolling with throttling
        def _on_mousewheel(event):
            current_time = int(time.time() * 1000)
            if current_time - self.last_draw_time > self.draw_throttle:
                self.graph_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                self.last_draw_time = current_time
        
        self.graph_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Add zoom controls with custom styling
        control_frame = ttk.Frame(graph_frame)
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights for control frame
        control_frame.grid_columnconfigure(3, weight=1)
        
        ttk.Button(control_frame, text="Zoom In", command=self.zoom_in).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Zoom Out", command=self.zoom_out).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Reset View", command=self.reset_view).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Save Graph", command=self.save_graph).grid(row=0, column=3, padx=5, sticky=tk.E)
        
    def create_text_section(self):
        text_frame = ttk.LabelFrame(self.main_container, text="Analysis Results", padding="10")
        text_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights for text frame
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Create text widget with scrollbar and custom styling
        self.text_widget = tk.Text(text_frame, 
                                 height=20, 
                                 width=50,
                                 bg=TOKYO_NIGHT['graph_bg'],
                                 fg=TOKYO_NIGHT['graph_text'],
                                 insertbackground=TOKYO_NIGHT['accent'],
                                 selectbackground=TOKYO_NIGHT['accent'],
                                 selectforeground=TOKYO_NIGHT['bg'])
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Copy button with custom styling
        ttk.Button(text_frame, text="Copy Analysis", command=self.copy_analysis).grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # List of encodings to try
                encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-16le', 'utf-16be']
                
                # Try different encodings
                for encoding in encodings:
                    try:
                        # First try with default settings
                        self.df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip')
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        # If we get a different error, try with different parameters
                        try:
                            # Try with different separators
                            for sep in [',', ';', '\t', '|']:
                                try:
                                    self.df = pd.read_csv(file_path, encoding=encoding, sep=sep, on_bad_lines='skip')
                                    if len(self.df.columns) > 1:  # Make sure we got multiple columns
                                        break
                                except:
                                    continue
                            if self.df is not None and len(self.df.columns) > 1:
                                break
                        except:
                            continue
                
                if self.df is None:
                    raise Exception("Could not read the file with any supported encoding")
                
                # Clean up the data
                self.clean_dataframe()
                
                # Update UI
                self.file_label.config(text=os.path.basename(file_path))
                messagebox.showinfo("Success", "CSV file loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error loading CSV file: {str(e)}")
                self.df = None
                
    def clean_dataframe(self):
        """Clean and prepare the dataframe for analysis"""
        try:
            # Remove any completely empty rows
            self.df = self.df.dropna(how='all')
            
            # Remove any completely empty columns
            self.df = self.df.dropna(axis=1, how='all')
            
            # Clean column names
            self.df.columns = [col.strip() for col in self.df.columns]
            
            # Try to identify and convert time columns
            time_columns = [col for col in self.df.columns if 'time' in col.lower()]
            date_columns = [col for col in self.df.columns if 'date' in col.lower()]
            
            # Handle time columns
            for col in time_columns:
                try:
                    # Try different time formats
                    time_formats = [
                        '%H:%M:%S', '%H:%M:%S.%f', '%I:%M:%S %p', 
                        '%I:%M:%S.%f %p', '%H:%M', '%I:%M %p'
                    ]
                    
                    for fmt in time_formats:
                        try:
                            self.df[col] = pd.to_datetime(self.df[col], format=fmt)
                            break
                        except:
                            continue
                            
                    # If none of the formats work, try general parsing
                    if not pd.api.types.is_datetime64_any_dtype(self.df[col]):
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                except:
                    continue
            
            # Handle date columns
            for col in date_columns:
                try:
                    # Try different date formats
                    date_formats = [
                        '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y',
                        '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y'
                    ]
                    
                    for fmt in date_formats:
                        try:
                            self.df[col] = pd.to_datetime(self.df[col], format=fmt)
                            break
                        except:
                            continue
                            
                    # If none of the formats work, try general parsing
                    if not pd.api.types.is_datetime64_any_dtype(self.df[col]):
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                except:
                    continue
            
            # Clean numeric columns
            for col in self.df.columns:
                if 'temperature' in col.lower() or 'temp' in col.lower() or 'usage' in col.lower():
                    try:
                        # Remove any non-numeric characters except decimal point
                        self.df[col] = self.df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                        # Convert to numeric, invalid values become NaN
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    except:
                        continue
            
            # Remove rows where all numeric columns are NaN
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                self.df = self.df.dropna(subset=numeric_cols, how='all')
            
        except Exception as e:
            print(f"Warning: Error during data cleaning: {str(e)}")
            # Continue with the data as is if cleaning fails
            
    def analyze_data(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a CSV file first!")
            return
            
        try:
            # Clear previous graph
            self.fig.clear()
            
            # Get selected options
            graph_type = self.graph_type.get()
            time_range = self.time_range.get()
            
            # Filter data based on time range
            if 'Time' in self.df.columns:
                self.df['Time'] = pd.to_datetime(self.df['Time'])
                if time_range != "All":
                    if time_range == "Morning (6AM-12PM)":
                        mask = (self.df['Time'].dt.hour >= 6) & (self.df['Time'].dt.hour < 12)
                    elif time_range == "Afternoon (12PM-6PM)":
                        mask = (self.df['Time'].dt.hour >= 12) & (self.df['Time'].dt.hour < 18)
                    elif time_range == "Evening (6PM-12AM)":
                        mask = (self.df['Time'].dt.hour >= 18) & (self.df['Time'].dt.hour < 24)
                    else:  # Night
                        mask = (self.df['Time'].dt.hour >= 0) & (self.df['Time'].dt.hour < 6)
                    filtered_df = self.df[mask]
                else:
                    filtered_df = self.df
            else:
                filtered_df = self.df
                
            # Create subplot
            ax = self.fig.add_subplot(111)
            
            # Plot based on graph type
            if graph_type == "Temperature":
                self.plot_temperatures(filtered_df, ax)
            elif graph_type == "CPU Usage":
                self.plot_cpu_usage(filtered_df, ax)
            elif graph_type == "GPU Usage":
                self.plot_gpu_usage(filtered_df, ax)
            else:  # All Metrics
                self.plot_all_metrics(filtered_df)
                
            # Update canvas
            self.canvas.draw()
            
            # Generate analysis text
            self.generate_analysis_text(filtered_df, graph_type)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during analysis: {str(e)}")
            
    def zoom_in(self):
        """Zoom in on the graph"""
        try:
            for ax in self.fig.axes:
                ax.set_xlim(ax.get_xlim()[0] * 0.8, ax.get_xlim()[1] * 0.8)
                ax.set_ylim(ax.get_ylim()[0] * 0.8, ax.get_ylim()[1] * 0.8)
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error", f"Error zooming in: {str(e)}")
            
    def zoom_out(self):
        """Zoom out on the graph"""
        try:
            for ax in self.fig.axes:
                ax.set_xlim(ax.get_xlim()[0] * 1.2, ax.get_xlim()[1] * 1.2)
                ax.set_ylim(ax.get_ylim()[0] * 1.2, ax.get_ylim()[1] * 1.2)
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error", f"Error zooming out: {str(e)}")
            
    def reset_view(self):
        """Reset the graph view to default"""
        try:
            self.analyze_data()  # This will redraw the graph with default settings
        except Exception as e:
            messagebox.showerror("Error", f"Error resetting view: {str(e)}")
            
    def plot_temperatures(self, df, ax):
        # Find temperature columns
        temp_cols = [col for col in df.columns if 'temperature' in col.lower() or 'temp' in col.lower()]
        
        # Use different colors for each line
        colors = [TOKYO_NIGHT['graph_line'], TOKYO_NIGHT['secondary'], TOKYO_NIGHT['success']]
        
        for i, col in enumerate(temp_cols):
            if 'time' in df.columns:
                ax.plot(df['Time'], df[col], label=col, color=colors[i % len(colors)])
            else:
                ax.plot(df.index, df[col], label=col, color=colors[i % len(colors)])
                
        ax.set_title("Temperature Analysis", color=TOKYO_NIGHT['graph_text'])
        ax.set_xlabel("Time", color=TOKYO_NIGHT['graph_text'])
        ax.set_ylabel("Temperature (°C)", color=TOKYO_NIGHT['graph_text'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adjust layout to prevent label cutoff
        self.fig.tight_layout()
        
    def plot_cpu_usage(self, df, ax):
        # Find CPU usage columns
        cpu_cols = [col for col in df.columns if 'cpu' in col.lower() and 'usage' in col.lower()]
        
        # Use different colors for each line
        colors = [TOKYO_NIGHT['graph_line'], TOKYO_NIGHT['secondary'], TOKYO_NIGHT['success']]
        
        for i, col in enumerate(cpu_cols):
            if 'time' in df.columns:
                ax.plot(df['Time'], df[col], label=col, color=colors[i % len(colors)])
            else:
                ax.plot(df.index, df[col], label=col, color=colors[i % len(colors)])
                
        ax.set_title("CPU Usage Analysis", color=TOKYO_NIGHT['graph_text'])
        ax.set_xlabel("Time", color=TOKYO_NIGHT['graph_text'])
        ax.set_ylabel("Usage (%)", color=TOKYO_NIGHT['graph_text'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adjust layout to prevent label cutoff
        self.fig.tight_layout()
        
    def plot_gpu_usage(self, df, ax):
        # Find GPU usage columns
        gpu_cols = [col for col in df.columns if 'gpu' in col.lower() and 'usage' in col.lower()]
        
        # Use different colors for each line
        colors = [TOKYO_NIGHT['graph_line'], TOKYO_NIGHT['secondary'], TOKYO_NIGHT['success']]
        
        for i, col in enumerate(gpu_cols):
            if 'time' in df.columns:
                ax.plot(df['Time'], df[col], label=col, color=colors[i % len(colors)])
            else:
                ax.plot(df.index, df[col], label=col, color=colors[i % len(colors)])
                
        ax.set_title("GPU Usage Analysis", color=TOKYO_NIGHT['graph_text'])
        ax.set_xlabel("Time", color=TOKYO_NIGHT['graph_text'])
        ax.set_ylabel("Usage (%)", color=TOKYO_NIGHT['graph_text'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adjust layout to prevent label cutoff
        self.fig.tight_layout()
        
    def plot_all_metrics(self, df):
        # Create subplots for different metrics
        gs = self.fig.add_gridspec(3, 1, height_ratios=[1, 1, 1])
        
        # Temperature subplot
        ax1 = self.fig.add_subplot(gs[0])
        self.plot_temperatures(df, ax1)
        
        # CPU usage subplot
        ax2 = self.fig.add_subplot(gs[1])
        self.plot_cpu_usage(df, ax2)
        
        # GPU usage subplot
        ax3 = self.fig.add_subplot(gs[2])
        self.plot_gpu_usage(df, ax3)
        
        # Adjust layout to prevent overlap
        self.fig.tight_layout()
        
    def generate_analysis_text(self, df, graph_type):
        self.text_widget.delete(1.0, tk.END)
        
        # Basic statistics
        self.text_widget.insert(tk.END, f"Analysis Results for {graph_type}\n")
        self.text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        if graph_type == "Temperature":
            temp_cols = [col for col in df.columns if 'temperature' in col.lower() or 'temp' in col.lower()]
            for col in temp_cols:
                stats = df[col].describe()
                self.text_widget.insert(tk.END, f"\n{col}:\n")
                self.text_widget.insert(tk.END, f"Average: {stats['mean']:.2f}°C\n")
                self.text_widget.insert(tk.END, f"Maximum: {stats['max']:.2f}°C\n")
                self.text_widget.insert(tk.END, f"Minimum: {stats['min']:.2f}°C\n")
                
        elif graph_type == "CPU Usage":
            cpu_cols = [col for col in df.columns if 'cpu' in col.lower() and 'usage' in col.lower()]
            for col in cpu_cols:
                stats = df[col].describe()
                self.text_widget.insert(tk.END, f"\n{col}:\n")
                self.text_widget.insert(tk.END, f"Average: {stats['mean']:.2f}%\n")
                self.text_widget.insert(tk.END, f"Maximum: {stats['max']:.2f}%\n")
                self.text_widget.insert(tk.END, f"Minimum: {stats['min']:.2f}%\n")
                
        elif graph_type == "GPU Usage":
            gpu_cols = [col for col in df.columns if 'gpu' in col.lower() and 'usage' in col.lower()]
            for col in gpu_cols:
                stats = df[col].describe()
                self.text_widget.insert(tk.END, f"\n{col}:\n")
                self.text_widget.insert(tk.END, f"Average: {stats['mean']:.2f}%\n")
                self.text_widget.insert(tk.END, f"Maximum: {stats['max']:.2f}%\n")
                self.text_widget.insert(tk.END, f"Minimum: {stats['min']:.2f}%\n")
                
        else:  # All Metrics
            self.text_widget.insert(tk.END, "Comprehensive System Analysis:\n\n")
            
            # Temperature analysis
            temp_cols = [col for col in df.columns if 'temperature' in col.lower() or 'temp' in col.lower()]
            if temp_cols:
                self.text_widget.insert(tk.END, "Temperature Analysis:\n")
                for col in temp_cols:
                    stats = df[col].describe()
                    self.text_widget.insert(tk.END, f"\n{col}:\n")
                    self.text_widget.insert(tk.END, f"Average: {stats['mean']:.2f}°C\n")
                    self.text_widget.insert(tk.END, f"Maximum: {stats['max']:.2f}°C\n")
                    self.text_widget.insert(tk.END, f"Minimum: {stats['min']:.2f}°C\n")
                    
            # CPU analysis
            cpu_cols = [col for col in df.columns if 'cpu' in col.lower() and 'usage' in col.lower()]
            if cpu_cols:
                self.text_widget.insert(tk.END, "\nCPU Usage Analysis:\n")
                for col in cpu_cols:
                    stats = df[col].describe()
                    self.text_widget.insert(tk.END, f"\n{col}:\n")
                    self.text_widget.insert(tk.END, f"Average: {stats['mean']:.2f}%\n")
                    self.text_widget.insert(tk.END, f"Maximum: {stats['max']:.2f}%\n")
                    self.text_widget.insert(tk.END, f"Minimum: {stats['min']:.2f}%\n")
                    
            # GPU analysis
            gpu_cols = [col for col in df.columns if 'gpu' in col.lower() and 'usage' in col.lower()]
            if gpu_cols:
                self.text_widget.insert(tk.END, "\nGPU Usage Analysis:\n")
                for col in gpu_cols:
                    stats = df[col].describe()
                    self.text_widget.insert(tk.END, f"\n{col}:\n")
                    self.text_widget.insert(tk.END, f"Average: {stats['mean']:.2f}%\n")
                    self.text_widget.insert(tk.END, f"Maximum: {stats['max']:.2f}%\n")
                    self.text_widget.insert(tk.END, f"Minimum: {stats['min']:.2f}%\n")
                    
    def save_graph(self):
        if not hasattr(self, 'fig'):
            messagebox.showwarning("Warning", "No graph to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", "Graph saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving graph: {str(e)}")
                
    def copy_analysis(self):
        if self.text_widget.get(1.0, tk.END).strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.text_widget.get(1.0, tk.END))
            messagebox.showinfo("Success", "Analysis copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No analysis to copy!")

    def show_statistical_analysis(self):
        """Show detailed statistical analysis"""
        if self.df is None:
            messagebox.showwarning("Warning", "Please load data first!")
            return
            
        # Create new window for statistical analysis
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistical Analysis")
        stats_window.geometry("600x400")
        
        # Create text widget for analysis
        text_widget = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Perform statistical analysis
        analysis_text = "Statistical Analysis Report\n"
        analysis_text += "=" * 30 + "\n\n"
        
        # Temperature analysis
        temp_cols = [col for col in self.df.columns if 'temperature' in col.lower() or 'temp' in col.lower()]
        if temp_cols:
            analysis_text += "Temperature Analysis:\n"
            for col in temp_cols:
                stats_data = self.df[col].describe()
                analysis_text += f"\n{col}:\n"
                analysis_text += f"Mean: {stats_data['mean']:.2f}°C\n"
                analysis_text += f"Std Dev: {stats_data['std']:.2f}°C\n"
                analysis_text += f"Min: {stats_data['min']:.2f}°C\n"
                analysis_text += f"Max: {stats_data['max']:.2f}°C\n"
                analysis_text += f"25th percentile: {stats_data['25%']:.2f}°C\n"
                analysis_text += f"75th percentile: {stats_data['75%']:.2f}°C\n"
        
        # CPU Usage analysis
        cpu_cols = [col for col in self.df.columns if 'cpu' in col.lower() and 'usage' in col.lower()]
        if cpu_cols:
            analysis_text += "\nCPU Usage Analysis:\n"
            for col in cpu_cols:
                stats_data = self.df[col].describe()
                analysis_text += f"\n{col}:\n"
                analysis_text += f"Mean: {stats_data['mean']:.2f}%\n"
                analysis_text += f"Std Dev: {stats_data['std']:.2f}%\n"
                analysis_text += f"Min: {stats_data['min']:.2f}%\n"
                analysis_text += f"Max: {stats_data['max']:.2f}%\n"
        
        # GPU Usage analysis
        gpu_cols = [col for col in self.df.columns if 'gpu' in col.lower() and 'usage' in col.lower()]
        if gpu_cols:
            analysis_text += "\nGPU Usage Analysis:\n"
            for col in gpu_cols:
                stats_data = self.df[col].describe()
                analysis_text += f"\n{col}:\n"
                analysis_text += f"Mean: {stats_data['mean']:.2f}%\n"
                analysis_text += f"Std Dev: {stats_data['std']:.2f}%\n"
                analysis_text += f"Min: {stats_data['min']:.2f}%\n"
                analysis_text += f"Max: {stats_data['max']:.2f}%\n"
        
        # Correlation analysis
        if len(temp_cols) > 0 and (len(cpu_cols) > 0 or len(gpu_cols) > 0):
            analysis_text += "\nCorrelation Analysis:\n"
            for temp_col in temp_cols:
                for cpu_col in cpu_cols:
                    corr = self.df[temp_col].corr(self.df[cpu_col])
                    analysis_text += f"\n{temp_col} vs {cpu_col}:\n"
                    analysis_text += f"Correlation coefficient: {corr:.2f}\n"
                for gpu_col in gpu_cols:
                    corr = self.df[temp_col].corr(self.df[gpu_col])
                    analysis_text += f"\n{temp_col} vs {gpu_col}:\n"
                    analysis_text += f"Correlation coefficient: {corr:.2f}\n"
        
        text_widget.insert(tk.END, analysis_text)
        text_widget.config(state=tk.DISABLED)
        
    def show_performance_trends(self):
        """Show performance trends analysis"""
        if self.df is None:
            messagebox.showwarning("Warning", "Please load data first!")
            return
            
        # Create new window for trends
        trends_window = tk.Toplevel(self.root)
        trends_window.title("Performance Trends")
        trends_window.geometry("800x600")
        
        # Create figure for trends
        fig = plt.Figure(figsize=(10, 8))
        canvas = FigureCanvasTkAgg(fig, master=trends_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create subplots
        gs = fig.add_gridspec(3, 1)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])
        
        # Plot trends
        if 'Time' in self.df.columns:
            time_data = self.df['Time']
        else:
            time_data = self.df.index
            
        # Temperature trends
        temp_cols = [col for col in self.df.columns if 'temperature' in col.lower() or 'temp' in col.lower()]
        for col in temp_cols:
            ax1.plot(time_data, self.df[col], label=col)
        ax1.set_title("Temperature Trends")
        ax1.set_ylabel("Temperature (°C)")
        ax1.legend()
        ax1.grid(True)
        
        # CPU usage trends
        cpu_cols = [col for col in self.df.columns if 'cpu' in col.lower() and 'usage' in col.lower()]
        for col in cpu_cols:
            ax2.plot(time_data, self.df[col], label=col)
        ax2.set_title("CPU Usage Trends")
        ax2.set_ylabel("Usage (%)")
        ax2.legend()
        ax2.grid(True)
        
        # GPU usage trends
        gpu_cols = [col for col in self.df.columns if 'gpu' in col.lower() and 'usage' in col.lower()]
        for col in gpu_cols:
            ax3.plot(time_data, self.df[col], label=col)
        ax3.set_title("GPU Usage Trends")
        ax3.set_xlabel("Time")
        ax3.set_ylabel("Usage (%)")
        ax3.legend()
        ax3.grid(True)
        
        fig.tight_layout()
        canvas.draw()
        
    def detect_anomalies(self):
        """Detect anomalies in the data"""
        if self.df is None:
            messagebox.showwarning("Warning", "Please load data first!")
            return
            
        # Create new window for anomalies
        anomalies_window = tk.Toplevel(self.root)
        anomalies_window.title("Anomaly Detection")
        anomalies_window.geometry("600x400")
        
        # Create text widget for anomalies
        text_widget = tk.Text(anomalies_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Detect anomalies using Z-score method
        anomalies_text = "Anomaly Detection Report\n"
        anomalies_text += "=" * 30 + "\n\n"
        
        # Temperature anomalies
        temp_cols = [col for col in self.df.columns if 'temperature' in col.lower() or 'temp' in col.lower()]
        if temp_cols:
            anomalies_text += "Temperature Anomalies:\n"
            for col in temp_cols:
                z_scores = np.abs(stats.zscore(self.df[col].dropna()))
                anomalies = self.df[z_scores > 3]  # Values more than 3 standard deviations
                if not anomalies.empty:
                    anomalies_text += f"\n{col}:\n"
                    for idx, row in anomalies.iterrows():
                        anomalies_text += f"Time: {idx}, Value: {row[col]:.2f}°C\n"
        
        # CPU usage anomalies
        cpu_cols = [col for col in self.df.columns if 'cpu' in col.lower() and 'usage' in col.lower()]
        if cpu_cols:
            anomalies_text += "\nCPU Usage Anomalies:\n"
            for col in cpu_cols:
                z_scores = np.abs(stats.zscore(self.df[col].dropna()))
                anomalies = self.df[z_scores > 3]
                if not anomalies.empty:
                    anomalies_text += f"\n{col}:\n"
                    for idx, row in anomalies.iterrows():
                        anomalies_text += f"Time: {idx}, Value: {row[col]:.2f}%\n"
        
        # GPU usage anomalies
        gpu_cols = [col for col in self.df.columns if 'gpu' in col.lower() and 'usage' in col.lower()]
        if gpu_cols:
            anomalies_text += "\nGPU Usage Anomalies:\n"
            for col in gpu_cols:
                z_scores = np.abs(stats.zscore(self.df[col].dropna()))
                anomalies = self.df[z_scores > 3]
                if not anomalies.empty:
                    anomalies_text += f"\n{col}:\n"
                    for idx, row in anomalies.iterrows():
                        anomalies_text += f"Time: {idx}, Value: {row[col]:.2f}%\n"
        
        text_widget.insert(tk.END, anomalies_text)
        text_widget.config(state=tk.DISABLED)
        
    def configure_alerts(self):
        """Configure alert thresholds"""
        # Create new window for alert configuration
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Configure Alerts")
        alert_window.geometry("300x200")
        
        # Create entry fields for thresholds
        ttk.Label(alert_window, text="Temperature Threshold (°C):").grid(row=0, column=0, padx=5, pady=5)
        temp_entry = ttk.Entry(alert_window)
        temp_entry.insert(0, str(self.alert_thresholds['temperature']))
        temp_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(alert_window, text="CPU Usage Threshold (%):").grid(row=1, column=0, padx=5, pady=5)
        cpu_entry = ttk.Entry(alert_window)
        cpu_entry.insert(0, str(self.alert_thresholds['cpu_usage']))
        cpu_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(alert_window, text="GPU Usage Threshold (%):").grid(row=2, column=0, padx=5, pady=5)
        gpu_entry = ttk.Entry(alert_window)
        gpu_entry.insert(0, str(self.alert_thresholds['gpu_usage']))
        gpu_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def save_thresholds():
            try:
                self.alert_thresholds['temperature'] = float(temp_entry.get())
                self.alert_thresholds['cpu_usage'] = float(cpu_entry.get())
                self.alert_thresholds['gpu_usage'] = float(gpu_entry.get())
                messagebox.showinfo("Success", "Alert thresholds updated!")
                alert_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        ttk.Button(alert_window, text="Save", command=save_thresholds).grid(row=3, column=0, columnspan=2, pady=10)
        
    def export_analysis(self):
        """Export analysis results to file"""
        if self.df is None:
            messagebox.showwarning("Warning", "Please load data first!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.text_widget.get(1.0, tk.END))
                messagebox.showinfo("Success", "Analysis exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting analysis: {str(e)}")
                
    def configure_graph_settings(self):
        """Configure graph display settings"""
        # Create new window for graph settings
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Graph Settings")
        settings_window.geometry("300x200")
        
        # Create settings options
        ttk.Label(settings_window, text="Graph Style:").grid(row=0, column=0, padx=5, pady=5)
        style_var = tk.StringVar(value="line")
        ttk.Radiobutton(settings_window, text="Line", variable=style_var, value="line").grid(row=0, column=1)
        ttk.Radiobutton(settings_window, text="Bar", variable=style_var, value="bar").grid(row=0, column=2)
        
        ttk.Label(settings_window, text="Show Grid:").grid(row=1, column=0, padx=5, pady=5)
        grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_window, variable=grid_var).grid(row=1, column=1)
        
        ttk.Label(settings_window, text="Show Legend:").grid(row=2, column=0, padx=5, pady=5)
        legend_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_window, variable=legend_var).grid(row=2, column=1)
        
        def apply_settings():
            # Update graph settings
            plt.style.use('dark_background')
            plt.rcParams.update({
                'axes.grid': grid_var.get(),
                'legend.frameon': legend_var.get()
            })
            # Redraw current graph
            self.analyze_data()
            settings_window.destroy()
            
        ttk.Button(settings_window, text="Apply", command=apply_settings).grid(row=3, column=0, columnspan=3, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = GamingAnalyzerGUI(root)
    root.mainloop() 