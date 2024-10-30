import re
import os
import shutil
import customtkinter as ctk
from customtkinter import *
from tkcalendar import Calendar, DateEntry
from CTkMessagebox import CTkMessagebox
import dbfile
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import hashlib

# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest().upper()

class Front:
    def __init__(self, master):
        self.obj = dbfile.OneUser()
        self.master = master
        self.master.title("SecureBank")
        self.login()

    def login(self):
        """Modern login page with three actions - LOGIN, CREATE, Forgot Password"""
        try:
            self.frame_body.pack_forget()
            self.frame_menu.pack_forget()
            self.frame_header.pack_forget()
        except:
            pass

        self.master.geometry('800x800')
        self.menu_count = 0
        
        # Header frame
        self.frame_header = ctk.CTkFrame(self.master)
        self.frame_header.pack(pady=20, padx=20, fill="x")
        
        # Center container for header content
        header_container = ctk.CTkFrame(self.frame_header, fg_color="transparent")
        header_container.pack(expand=True)
        
        # Load and resize logo
        self.logo = Image.open('python_logo.gif')
        self.logo = self.logo.resize((60, 60))
        self.logo = ImageTk.PhotoImage(self.logo)
        
        # Logo and title in header
        ctk.CTkLabel(header_container, image=self.logo, text="").pack(pady=10)
        ctk.CTkLabel(header_container, 
                    text='Welcome to SecureBank',
                    font=("Helvetica", 24, "bold")).pack(pady=10)

        # Body frame
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Center container for login form
        form_container = ctk.CTkFrame(self.frame_body, fg_color="transparent")
        form_container.pack(expand=True)

        # Login form items
        username_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        username_frame.pack(pady=10)
        ctk.CTkLabel(username_frame, text='Username:').pack(side="left", padx=10)
        self.user = ctk.CTkEntry(username_frame, width=200, placeholder_text="Enter username")
        self.user.pack(side="left", padx=10)

        password_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        password_frame.pack(pady=10)
        ctk.CTkLabel(password_frame, text='Password:').pack(side="left", padx=10)
        self.psd = ctk.CTkEntry(password_frame, width=200, show="●", placeholder_text="Enter password")
        self.psd.pack(side="left", padx=10)

        def temp_action():  # Removed self parameter since it's already in closure scope
            """Login validation with password hashing"""
            self.log_name = self.user.get()
            self.log_pass = hash_password(self.psd.get())

            try:
                self.uid, self.vname, self.vemail, self.vaddress, self.vdob, self.vphone, self.vpass, self.vupi, \
                self.vrecent, self.profile_photo, self.ouid, self.vbank, self.vacc, self.vbal = self.obj.get_details(self.log_name)

                if self.log_name == self.vname and self.log_pass == self.vpass:
                    CTkMessagebox(title="Welcome", message=f"Welcome {self.log_name}", icon="info")
                    self.home()
                else:
                    CTkMessagebox(title="Error", message="Invalid username or password", icon="cancel")
            except:
                CTkMessagebox(title="Error", message="User not found", icon="cancel")
                
        # Button container
        button_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Login", command=temp_action).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Create Account", command=self.create).pack(side="left", padx=10)
        
        # Forgot password link
        ctk.CTkButton(form_container, 
                     text="Forgot Password?", 
                     command=self.forgot,
                     fg_color="transparent", 
                     text_color=("gray10", "gray90")).pack(pady=10)

    def forgot(self):
        """Modern forgot password page with OTP functionality"""
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Email entry
        ctk.CTkLabel(self.frame_body, text='Enter email address:',
                    font=("Helvetica", 14)).pack(pady=10)
        self.otpemail = ctk.CTkEntry(self.frame_body, width=300, 
                                    placeholder_text="your.email@example.com")
        self.otpemail.pack(pady=10)

        def on_click_email():
            if self.obj.send_otp(self.otpemail.get()) == 1:
                CTkMessagebox(title="Success", 
                            message=f"OTP sent to: {self.otpemail.get()}", 
                            icon="info")
                self.otppage()
            else:
                CTkMessagebox(title="Error", 
                            message="Email not found in our records", 
                            icon="cancel")

        button_frame = ctk.CTkFrame(self.frame_body)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Send OTP", 
                     command=on_click_email).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Back", 
                     command=self.already,
                     fg_color="transparent").pack(side="left", padx=10)

    def otppage(self):
        """Modern OTP verification page"""
        def temp_otp_action():
            self.otpvalue = self.otpvalue.get()
            if self.obj.check_otp(self.otpvalue):
                self.change_pass_in_otp()
            else:
                CTkMessagebox(title="Error", message="Invalid OTP", icon="cancel")
                self.already()

        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.frame_body, text='Enter OTP:', 
                    font=("Helvetica", 14)).pack(pady=10)
        self.otpvalue = ctk.CTkEntry(self.frame_body, width=200, 
                                    placeholder_text="Enter 6-digit OTP")
        self.otpvalue.pack(pady=10)

        button_frame = ctk.CTkFrame(self.frame_body)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Verify", 
                     command=temp_otp_action).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancel", 
                     command=self.already,
                     fg_color="transparent").pack(side="left", padx=10)
                     
    def change_pass_in_otp(self):
        """Password change page after OTP verification"""
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.uid, self.vname, self.vemail, self.vaddress, self.vdob, self.vphone, self.vpass, self.vupi, \
        self.vrecent, self.profile_photo, self.ouid, self.vbank, self.vacc, self.vbal = self.obj.get_details_email()
        
        self.password_change()

        def temp_pass_action():
            if self.edit_sp.get() == self.edit_fp.get():
                hashed_new = hash_password(self.edit_fp.get())
                self.obj.otp_change_password(self.otpemail.get(), hashed_new)
                CTkMessagebox(title="Success", message="Password changed successfully", icon="check")
                self.home()
            else:
                CTkMessagebox(title="Error", message="Passwords don't match", icon="cancel")

        button_frame = ctk.CTkFrame(self.frame_body)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Save", command=temp_pass_action).pack(side="left", padx=10)

    def edit_photo(self):
        """Profile photo editor with modern file dialog"""
        import shutil
        import os
        
        filetypes = (
            ('Image files', '*.jpg'),
            ('Image files', '*.png'),
            ('Image files', '*.jpeg'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Select Profile Picture',
            initialdir='/',
            filetypes=filetypes
        )
        
        if filename:
            try:
                # Create profile_images directory if it doesn't exist
                if not os.path.exists("profile_images"):
                    os.makedirs("profile_images")
                
                # Copy the selected file to profile_images directory with user's name
                destination = os.path.join("profile_images", f"{self.vname}.jpg")
                
                # If the file is not a JPEG, convert it
                if not filename.lower().endswith('.jpg'):
                    from PIL import Image
                    img = Image.open(filename)
                    # Convert to RGB if necessary (in case of PNG with alpha channel)
                    if img.mode in ('RGBA', 'LA'):
                        bg = Image.new('RGB', img.size, 'white')
                        bg.paste(img, mask=img.split()[-1])
                        img = bg
                    img.save(destination, 'JPEG', quality=95)
                else:
                    shutil.copy2(filename, destination)
                
                # Update the display
                self.profile()
                
            except Exception as e:
                CTkMessagebox(title="Error", 
                             message=f"Failed to update profile picture: {str(e)}", 
                             icon="cancel")

    def create_photo(self):
        """Profile photo creation for new accounts"""
        import shutil
        import os
        
        filetypes = (
            ('Image files', '*.jpg'),
            ('Image files', '*.png'),
            ('Image files', '*.jpeg'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Select Profile Picture',
            initialdir='/',
            filetypes=filetypes
        )
        
        if filename:
            try:
                # Store the selected filename to be processed after account creation
                self.temp_profile_image = filename
            except Exception as e:
                CTkMessagebox(title="Error", 
                             message=f"Failed to select profile picture: {str(e)}", 
                             icon="cancel")

    def menu_ini(self):
        """Initialize the main navigation menu"""
        self.frame_menu = ctk.CTkFrame(self.master)
        self.frame_menu.pack(pady=10, padx=20, fill="x")
        
        # Create a container for menu buttons
        button_container = ctk.CTkFrame(self.frame_menu)
        button_container.pack(expand=True)
        
        # Menu buttons with consistent styling
        button_style = {"width": 120, "height": 32, "corner_radius": 8}
        
        self.homebut = ctk.CTkButton(button_container, text="Home", 
                                    command=self.home, **button_style)
        self.homebut.pack(side="left", padx=5)
        
        self.probut = ctk.CTkButton(button_container, text="Profile", 
                                   command=self.profile, **button_style)
        self.probut.pack(side="left", padx=5)
        
        self.fribut = ctk.CTkButton(button_container, text="Friends", 
                                   command=self.friends, **button_style)
        self.fribut.pack(side="left", padx=5)
        
        self.tranbut = ctk.CTkButton(button_container, text="Transfer", 
                                    command=self.transfer, **button_style)
        self.tranbut.pack(side="left", padx=5)
        
        self.seabut = ctk.CTkButton(button_container, text="Search", 
                                   command=self.search, **button_style)
        self.seabut.pack(side="left", padx=5)

    def home(self):
        """Modern home page with profile display and main actions"""
        if self.menu_count == 0:
            self.menu_ini()
            self.menu_count = 1

        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Profile section
        profile_frame = ctk.CTkFrame(self.frame_body)
        profile_frame.pack(pady=20, fill="x", padx=20)

        # Load profile image
        try:
            profile_img = self.get_profile_image(self.vname)
            if profile_img:
                profile_img = profile_img.resize((100, 100))
                self.profile_image = ImageTk.PhotoImage(profile_img)
                ctk.CTkLabel(profile_frame, image=self.profile_image, text="").pack(side="left", padx=20)
        except Exception as e:
            print(f"Error displaying profile image in home: {e}")

        # Welcome message
        message_frame = ctk.CTkFrame(profile_frame)
        message_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        ctk.CTkLabel(message_frame, 
                    text=f"Welcome to SecureBank",
                    font=("Helvetica", 20, "bold")).pack(anchor="w", pady=5)
        
        ctk.CTkLabel(message_frame, 
                    text="Your trusted banking partner for secure and swift transactions.",
                    wraplength=400).pack(anchor="w")

        # Actions section
        actions_frame = ctk.CTkFrame(self.frame_body)
        actions_frame.pack(pady=20, fill="x", padx=20)
        
        # Grid of main action buttons
        button_style = {
            "width": 200,
            "height": 40,
            "corner_radius": 8,
            "font": ("Helvetica", 14)
        }
        
        ctk.CTkButton(actions_frame, 
                     text="Check Balance",
                     command=self.check_balance,
                     **button_style).pack(pady=10)
                     
        ctk.CTkButton(actions_frame,
                     text="Recent Transactions",
                     command=self.transaction_history,
                     **button_style).pack(pady=10)
                     
        ctk.CTkButton(actions_frame,
                     text="Usage Graph",
                     command=self.graphpage,
                     **button_style).pack(pady=10)
                     
        ctk.CTkButton(actions_frame,
                     text="Logout",
                     command=self.login,
                     fg_color="transparent",
                     text_color=("gray10", "gray90"),
                     **button_style).pack(pady=10)

    def graphpage(self):
        """Transaction history visualization with matplotlib"""
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.user_list = self.obj.retrieve_recent(self.uid)
        
        if self.user_list:
            self.user_list = eval(self.user_list)
            n = len(self.user_list)
            
            # Header buttons
            button_frame = ctk.CTkFrame(self.frame_body)
            button_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkButton(button_frame, text="Back", 
                         command=self.home).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Clear History",
                         command=self.clear_usage,
                         fg_color="transparent").pack(side="left", padx=5)

            # Create matplotlib figure
            fig = Figure(figsize=(8, 6), facecolor='#2b2b2b')
            plot1 = fig.add_subplot(111)
            
            # Style the plot
            plot1.plot(range(n), self.user_list, color='#3b8ed0', linewidth=2)
            plot1.set_xlabel('Transactions', color='white')
            plot1.set_ylabel('Balance After Transaction', color='white')
            plot1.tick_params(colors='white')
            plot1.grid(True, linestyle='--', alpha=0.3)
            plot1.set_facecolor('#2b2b2b')
            
            # Embed the plot
            canvas = FigureCanvasTkAgg(fig, master=self.frame_body)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
            
        else:
            self.master.geometry('800x800')
            ctk.CTkLabel(self.frame_body, 
                        text="No transaction history available",
                        font=("Helvetica", 16)).pack(pady=20)
            ctk.CTkButton(self.frame_body, text='Back',
                         command=self.home).pack(pady=10)
                         
    def clear_usage(self):
        """Clear transaction history with confirmation"""
        dialog = CTkMessagebox(
            title="Clear History",
            message="Are you sure you want to clear your usage history?",
            icon="warning",
            option_1="Cancel",
            option_2="Clear"
        )
        
        if dialog.get() == "Clear":
            self.obj.clear_recent(self.uid)
            self.home()

    def create(self):
        """Modern account creation form with scrollable frame"""
        self.master.geometry('800x800')

        self.frame_body.pack_forget()
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Title
        ctk.CTkLabel(self.frame_body, 
                    text="Create New Account",
                    font=("Helvetica", 24, "bold")).pack(pady=20)

        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.frame_body)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Personal Information Section
        personal_frame = ctk.CTkFrame(scroll_frame)
        personal_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(personal_frame, 
                    text="Personal Information",
                    font=("Helvetica", 18, "bold")).pack(pady=10)

        # Create grid for personal details
        grid_frame = ctk.CTkFrame(personal_frame)
        grid_frame.pack(fill="x", padx=20, pady=10)

        # Personal details entries
        entries = [
            ("Name:", "name", "Enter your full name"),
            ("Email:", "email", "Enter your email address"),
            ("Mobile:", "phone", "Enter your phone number"),
            ("Address:", "address", "Enter your full address")
        ]

        for i, (label_text, attr_name, placeholder) in enumerate(entries):
            entry_frame = ctk.CTkFrame(grid_frame)
            entry_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(entry_frame, 
                        text=label_text,
                        font=("Helvetica", 14),
                        width=120,
                        anchor="e").pack(side="left", padx=10)
                        
            entry = ctk.CTkEntry(entry_frame, 
                                placeholder_text=placeholder,
                                width=250)
            entry.pack(side="left", padx=10)
            setattr(self, attr_name, entry)

        # Date of Birth
        dob_frame = ctk.CTkFrame(grid_frame)
        dob_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(dob_frame, 
                    text="Date of Birth:",
                    font=("Helvetica", 14),
                    width=120,
                    anchor="e").pack(side="left", padx=10)
                    
        self.dob = DateEntry(dob_frame, 
                            width=18, 
                            background='darkblue',
                            foreground='white',
                            borderwidth=2,
                            year=2000,
                            month=1,
                            day=1,
                            date_pattern='dd/MM/yyyy')
        self.dob.pack(side="left", padx=10)

        # Banking Information Section
        bank_frame = ctk.CTkFrame(scroll_frame)
        bank_frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(bank_frame, 
                    text="Banking Information",
                    font=("Helvetica", 18, "bold")).pack(pady=10)

        bank_details_frame = ctk.CTkFrame(bank_frame)
        bank_details_frame.pack(fill="x", padx=20, pady=10)

        # Bank selection
        bank_select_frame = ctk.CTkFrame(bank_details_frame)
        bank_select_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(bank_select_frame,
                    text="Bank:",
                    font=("Helvetica", 14),
                    width=120,
                    anchor="e").pack(side="left", padx=10)
                    
        self.bankoptions = ['Chase', 'Bank of America', 'Wells Fargo', 'Citibank']
        self.bank = ctk.CTkOptionMenu(bank_select_frame,
                                     values=self.bankoptions,
                                     width=250)
        self.bank.pack(side="left", padx=10)
        self.bank.set('Select your bank')

        # Account fields
        account_entries = [
            ("Account Number:", "acc", "Enter your account number"),
            ("Create Password:", "pswd", "Enter a strong password"),
            ("Confirm Password:", "repswd", "Confirm your password"),
            ("Create UPI PIN:", "upi", "Create 4-digit UPI PIN"),
            ("Confirm UPI PIN:", "reupi", "Confirm UPI PIN")
        ]

        for label_text, attr_name, placeholder in account_entries:
            entry_frame = ctk.CTkFrame(bank_details_frame)
            entry_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(entry_frame,
                        text=label_text,
                        font=("Helvetica", 14),
                        width=120,
                        anchor="e").pack(side="left", padx=10)
                        
            entry = ctk.CTkEntry(entry_frame,
                                placeholder_text=placeholder,
                                width=250,
                                show="●" if "pswd" in attr_name or "upi" in attr_name else None)
            entry.pack(side="left", padx=10)
            setattr(self, attr_name, entry)

        # Profile Picture Section
        photo_frame = ctk.CTkFrame(scroll_frame)
        photo_frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(photo_frame,
                    text="Profile Picture",
                    font=("Helvetica", 18, "bold")).pack(pady=10)
                    
        ctk.CTkButton(photo_frame,
                     text="Upload Profile Picture",
                     command=self.create_photo).pack(pady=10)

        # Action Buttons Section (outside scroll frame)
        button_frame = ctk.CTkFrame(self.frame_body)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame,
                     text='Create Account',
                     command=self.temp_action2).pack(side="left", padx=10)
                     
        ctk.CTkButton(button_frame,
                     text='Cancel',
                     command=self.edit_cancel_create,
                     fg_color="transparent").pack(side="left", padx=10)

        # Sign-in link
        sign_in_frame = ctk.CTkFrame(self.frame_body)
        sign_in_frame.pack(pady=10)
        
        ctk.CTkLabel(sign_in_frame,
                    text='Already have an account?').pack(pady=5)
                    
        ctk.CTkButton(sign_in_frame,
                     text='Sign In',
                     command=self.already,
                     fg_color="transparent").pack()

    def already(self):
        """Return to login page"""
        self.frame_header.pack_forget()
        self.frame_body.pack_forget()
        self.login()
            
    def temp_action2(self):
        # Get values from form
        self.vname = self.name.get()
        self.vemail = self.email.get()
        self.vdob = self.dob.get()
        self.vphone = self.phone.get()
        self.vaddress = self.address.get()
        self.vfirstpass = self.pswd.get()
        self.vsecondpass = self.repswd.get()
        self.vupi = self.upi.get()
        self.vreupi = self.reupi.get()
        self.vbank = self.bank.get()
        self.vacc = self.acc.get()

        # Validation
        if not self.vname.replace(" ", "").isalpha():
            CTkMessagebox(title="Error", message="Please enter a valid name", icon="cancel")
            return

        # Email validation
        pattern = re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|edu|net)', self.vemail)
        if not pattern:
            CTkMessagebox(title="Error", message="Please enter a valid email address", icon="cancel")
            return

        if not self.vphone.isdigit() or len(self.vphone) != 10:
            CTkMessagebox(title="Error", message="Please enter a valid 10-digit phone number", icon="cancel")
            return

        if self.vfirstpass != self.vsecondpass:
            CTkMessagebox(title="Error", message="Passwords don't match", icon="cancel")
            return

        if self.vbank not in self.bankoptions:
            CTkMessagebox(title="Error", message="Please select a valid bank", icon="cancel")
            return
            
        if not self.vacc.isdigit() or len(self.vacc) != 8:
            CTkMessagebox(title="Error", message="Please enter a valid 8-digit account number", icon="cancel")
            return

        if self.vupi != self.vreupi:
            CTkMessagebox(title="Error", message="UPI PINs don't match", icon="cancel")
            return
        
        # Hash password and UPI before storage
        hashed_password = hash_password(self.vfirstpass)
        hashed_upi = hash_password(self.vupi)
        
        # Process account creation
        result = self.obj.insert_record(self.vname, self.vemail, self.vdob, self.vphone, 
                                      self.vaddress, hashed_password, hashed_upi, 
                                      self.vbank, self.vacc)
        
        if result == 1:
            CTkMessagebox(title="Success", 
                         message=f"Welcome to SecureBank, {self.vname}!", 
                         icon="check")
            
            self.uid, self.vname, self.vemail, self.vaddress, self.vdob, self.vphone, \
            self.vpass, self.vupi, self.vrecent, self.profile_photo, self.ouid, \
            self.vbank, self.vacc, self.vbal = self.obj.get_details(self.vname)
            
            # Handle profile picture if one was selected
            if hasattr(self, 'temp_profile_image') and self.temp_profile_image:
                try:
                    # Create profile_images directory if it doesn't exist
                    if not os.path.exists("profile_images"):
                        os.makedirs("profile_images")
                    
                    destination = os.path.join("profile_images", f"{self.vname}.jpg")
                    
                    # If the file is not a JPEG, convert it
                    if not self.temp_profile_image.lower().endswith('.jpg'):
                        img = Image.open(self.temp_profile_image)
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'LA'):
                            bg = Image.new('RGB', img.size, 'white')
                            bg.paste(img, mask=img.split()[-1])
                            img = bg
                        img.save(destination, 'JPEG', quality=95)
                    else:
                        shutil.copy2(self.temp_profile_image, destination)
                    
                except Exception as e:
                    print(f"Error saving profile picture: {e}")
            
            self.home()
        else:
            CTkMessagebox(title="Error", 
                         message="This account number is not registered with the selected bank", 
                         icon="cancel")

    def text_for_check(self):
        """UPI verification dialog"""
        self.frame_body.pack_forget()
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        verification_frame = ctk.CTkFrame(self.frame_body)
        verification_frame.pack(expand=True, padx=20, pady=20)

        ctk.CTkLabel(verification_frame, 
                    text="Enter your UPI PIN:",
                    font=("Helvetica", 14, "bold")).pack(pady=10)
                    
        self.check_upi = ctk.CTkEntry(verification_frame, 
                                     show="●", 
                                     width=200,
                                     placeholder_text="Enter 4-digit UPI PIN")
        self.check_upi.pack(pady=10)

    def check_balance(self):
        """Check balance with UPI verification"""
        self.text_for_check()
        
        ctk.CTkButton(self.frame_body, 
                     text='Verify', 
                     command=self.check_balance2).pack(pady=10)

    def check_balance2(self):
        """Display balance after UPI verification"""
        self.hereamount = self.upi_validation()
        
        if self.hereamount == -1:
            CTkMessagebox(title="Error", 
                         message="Invalid UPI PIN", 
                         icon="cancel")
            self.home()
        else:
            # Create a new frame for balance display
            balance_frame = ctk.CTkFrame(self.frame_body)
            balance_frame.pack(expand=True, padx=20, pady=20)

            ctk.CTkLabel(balance_frame, 
                        text="Current Balance",
                        font=("Helvetica", 18, "bold")).pack(pady=10)
                        
            ctk.CTkLabel(balance_frame, 
                        text=f"${self.hereamount:,.2f}",
                        font=("Helvetica", 24)).pack(pady=10)

            ctk.CTkButton(balance_frame, 
                         text='Return to Home', 
                         command=self.home).pack(pady=20)

    def upi_validation(self):
        """Validate UPI and return balance"""
        self.frame_body.pack_forget()
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.upi_val = hash_password(self.check_upi.get())
        self.amount = self.obj.check_balance(self.uid, self.upi_val)
        return self.amount
        
    def transaction_history(self):
        """Display transaction history with modern UI"""
        self.frame_body.pack_forget()
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Header
        header_frame = ctk.CTkFrame(self.frame_body)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(header_frame, 
                    text="Transaction History",
                    font=("Helvetica", 20, "bold")).pack()

        # Scrollable transaction list
        scroll_frame = ctk.CTkScrollableFrame(self.frame_body)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.vals = self.obj.transaction_history(self.vacc)
        
        for transaction in self.vals:
            transaction_frame = ctk.CTkFrame(scroll_frame)
            transaction_frame.pack(fill="x", pady=5)
            
            if str(transaction[0]) == self.vacc:  # Sent transaction
                amount_text = f"-${transaction[2]:,.2f}"
                description = f"Sent to {transaction[5]}"
                color = "#FF6B6B"  # Red for sent
            else:  # Received transaction
                amount_text = f"+${transaction[2]:,.2f}"
                description = f"Received from {transaction[4]}"
                color = "#4CAF50"  # Green for received

            ctk.CTkLabel(transaction_frame,
                        text=amount_text,
                        text_color=color,
                        font=("Helvetica", 16, "bold")).pack(side="left", padx=10)
                        
            details_frame = ctk.CTkFrame(transaction_frame)
            details_frame.pack(side="left", fill="both", expand=True)
            
            ctk.CTkLabel(details_frame,
                        text=description,
                        font=("Helvetica", 14)).pack(anchor="w", padx=10)
                        
            ctk.CTkLabel(details_frame,
                        text=transaction[3][:19],
                        font=("Helvetica", 12),
                        text_color="gray").pack(anchor="w", padx=10)

        # Back button
        ctk.CTkButton(self.frame_body,
                     text="Return to Home",
                     command=self.home).pack(pady=10)

    def transaction_history_friend(self, value):
        """Display transaction history with a specific friend"""
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Friend info header
        header_frame = ctk.CTkFrame(self.frame_body)
        header_frame.pack(fill="x", padx=20, pady=10)

        facc, _ = self.obj.friend_info(value)  # We don't need friend_obj anymore since we're using file-based images
        
        # Try to load friend's profile image
        try:
            friend_img = self.get_profile_image(value)
            if friend_img:
                friend_img = friend_img.resize((80, 80))
                self.friend_image = ImageTk.PhotoImage(friend_img)
                ctk.CTkLabel(header_frame, image=self.friend_image, text="").pack(side="left", padx=10)
        except Exception as e:
            print(f"Error loading friend's profile image: {e}")
                
        ctk.CTkLabel(header_frame,
                    text=value,
                    font=("Helvetica", 18, "bold")).pack(side="left", padx=10)
        
        ctk.CTkLabel(header_frame,
                    text="Transaction History",
                    font=("Helvetica", 16)).pack(side="right", padx=10)

        # Scrollable transaction list
        scroll_frame = ctk.CTkScrollableFrame(self.frame_body)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.vals = self.obj.transaction_history(self.vacc)
        
        if not self.vals:
            ctk.CTkLabel(scroll_frame,
                        text="No transaction history available",
                        font=("Helvetica", 14)).pack(pady=20)
            return

        for transaction in self.vals:
            if (str(transaction[0]) == self.vacc and str(transaction[1]) == facc) or \
               (str(transaction[1]) == self.vacc and str(transaction[0]) == facc):
                   
                transaction_frame = ctk.CTkFrame(scroll_frame)
                transaction_frame.pack(fill="x", pady=5)
                
                if str(transaction[0]) == self.vacc:  # Sent
                    amount_text = f"-${transaction[2]:,.2f}"
                    description = f"Sent to {transaction[5]}"
                    color = "#FF6B6B"
                else:  # Received
                    amount_text = f"+${transaction[2]:,.2f}"
                    description = f"Received from {transaction[4]}"
                    color = "#4CAF50"

                ctk.CTkLabel(transaction_frame,
                            text=amount_text,
                            text_color=color,
                            font=("Helvetica", 16, "bold")).pack(side="left", padx=10)
                            
                details_frame = ctk.CTkFrame(transaction_frame)
                details_frame.pack(side="left", fill="both", expand=True)
                
                ctk.CTkLabel(details_frame,
                            text=description,
                            font=("Helvetica", 14)).pack(anchor="w", padx=10)
                            
                ctk.CTkLabel(details_frame,
                            text=transaction[3][:19],
                            font=("Helvetica", 12),
                            text_color="gray").pack(anchor="w", padx=10)

                            
    def friends(self):
        """Modern friends list with payment functionality"""
        def pay_friend(value):
            """Dialog to pay selected friend"""
            self.frame_body.pack_forget()
            self.frame_body = ctk.CTkFrame(self.master)
            self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

            payment_frame = ctk.CTkFrame(self.frame_body)
            payment_frame.pack(expand=True, padx=20, pady=20)

            ctk.CTkLabel(payment_frame, 
                        text=f"Send Money to {value}",
                        font=("Helvetica", 18, "bold")).pack(pady=10)

            amount_frame = ctk.CTkFrame(payment_frame)
            amount_frame.pack(pady=20)

            ctk.CTkLabel(amount_frame, text="Amount: $",
                        font=("Helvetica", 14)).pack(side="left", padx=5)
                        
            self.money_tran_friend = ctk.CTkEntry(amount_frame, 
                                                 width=200,
                                                 placeholder_text="Enter amount")
            self.money_tran_friend.pack(side="left", padx=5)

            button_frame = ctk.CTkFrame(payment_frame)
            button_frame.pack(pady=20)

            ctk.CTkButton(button_frame, 
                         text='Send',
                         command=lambda: self.pay_tran_friend(value)).pack(side="left", padx=10)
                         
            ctk.CTkButton(button_frame, 
                         text='Cancel',
                         command=self.friends,
                         fg_color="transparent").pack(side="left", padx=10)

        def pay_friend_interm(value):
            self.transaction_history_friend(value)
            
            button_frame = ctk.CTkFrame(self.frame_body)
            button_frame.pack(pady=20)
            
            ctk.CTkButton(button_frame,
                         text='Send Money',
                         command=lambda: pay_friend(value)).pack(side="left", padx=10)
                         
            ctk.CTkButton(button_frame,
                         text='Back',
                         command=self.friends,
                         fg_color="transparent").pack(side="left", padx=10)

        # Main friends list UI
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Header
        ctk.CTkLabel(self.frame_body, 
                    text="Friends",
                    font=("Helvetica", 24, "bold")).pack(pady=20)

        # Create scrollable frame for friends list
        scroll_frame = ctk.CTkScrollableFrame(self.frame_body)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Get unique friends from transaction history
        self.vals = self.obj.transaction_history(self.vacc)
        self.friend_set = set()
        
        for transaction in self.vals:
            if str(transaction[0]) == self.vacc:
                self.friend_set.add(transaction[5])
            elif str(transaction[1]) == self.vacc:
                self.friend_set.add(transaction[4])
                    
        self.friend_set.discard(self.vname)
        self.friend_list = list(self.friend_set)

        if not self.friend_list:
            ctk.CTkLabel(scroll_frame,
                        text="No friends yet. Start by making a transaction!",
                        font=("Helvetica", 14)).pack(pady=20)
        else:
            for friend in self.friend_list:
                friend_frame = ctk.CTkFrame(scroll_frame)
                friend_frame.pack(fill="x", pady=5, padx=10)
                
                # Load friend's profile image
                try:
                    friend_img = self.get_profile_image(friend)
                    if friend_img:
                        friend_img = friend_img.resize((40, 40))
                        friend_photo = ImageTk.PhotoImage(friend_img)
                        ctk.CTkLabel(friend_frame, image=friend_photo, text="").pack(side="left", padx=5)
                        # Store the photo reference to prevent garbage collection
                        setattr(self, f"friend_photo_{friend}", friend_photo)
                except Exception as e:
                    print(f"Error displaying friend image for {friend}: {e}")
                
                ctk.CTkButton(friend_frame,
                             text=friend,
                             command=lambda f=friend: pay_friend_interm(f),
                             height=40,
                             fg_color="transparent",
                             hover_color=("gray75", "gray25")).pack(fill="x", padx=5, pady=5)

    def pay_tran_friend(self, value):
        """Process friend payment with UPI verification"""
        self.text_for_check()
        
        ctk.CTkButton(self.frame_body,
                     text='Verify',
                     command=lambda: self.after_pay_tran_friend(value)).pack(pady=10)

    def after_pay_tran_friend(self, value):
        """Complete friend payment after verification"""
        self.hereamount = self.upi_validation()
        
        if self.hereamount == -1:
            CTkMessagebox(title="Error", 
                         message="Invalid UPI PIN",
                         icon="cancel")
            self.friends()
            return
            
        friendmoney = self.money_tran_friend.get()
        
        if not friendmoney.isdigit():
            CTkMessagebox(title="Error", 
                         message="Please enter a valid amount",
                         icon="cancel")
            return
            
        dialog = CTkMessagebox(
            title="Confirm Payment",
            message=f"Send ${float(friendmoney):,.2f} to {value}?",
            icon="question",
            option_1="Cancel",
            option_2="Send"
        )
        
        if dialog.get() == "Send":
            self.return_tran = self.obj.pay_friend(self.uid, self.vname, value, int(friendmoney))
            
            if self.return_tran == 'lowbal':
                CTkMessagebox(title="Error", 
                             message="Insufficient funds",
                             icon="cancel")
            elif self.return_tran == -1:
                CTkMessagebox(title="Error", 
                             message="Transaction failed. Please try again.",
                             icon="cancel")
            else:
                CTkMessagebox(title="Success", 
                             message="Payment sent successfully!",
                             icon="check")
                self.friends()

    def transfer(self):
        """Money transfer interface"""
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Title
        ctk.CTkLabel(self.frame_body,
                    text="Send Money",
                    font=("Helvetica", 24, "bold")).pack(pady=20)

        # Transfer form
        form_frame = ctk.CTkFrame(self.frame_body)
        form_frame.pack(expand=True, padx=20, pady=20)

        # Account number entry
        acc_frame = ctk.CTkFrame(form_frame)
        acc_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(acc_frame,
                     text="Account Number:",
                     font=("Helvetica", 14)).pack(side="left", padx=10)

        self.acc_tran = ctk.CTkEntry(acc_frame,
                                    width=250,
                                    placeholder_text="Enter recipient's account number")
        self.acc_tran.pack(side="right", padx=10)

        # Amount entry
        amount_frame = ctk.CTkFrame(form_frame)
        amount_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(amount_frame,
                     text="Amount: $",
                     font=("Helvetica", 14)).pack(side="left", padx=10)

        self.money_tran = ctk.CTkEntry(amount_frame,
                                      width=250,
                                      placeholder_text="Enter amount to send")
        self.money_tran.pack(side="right", padx=10)

        # Buttons
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame,
                     text='Send',
                     command=self.pay_tran).pack(side="left", padx=10)
                     
        ctk.CTkButton(button_frame,
                     text='Cancel',
                     command=self.edit_cancel2,
                     fg_color="transparent").pack(side="left", padx=10)

    def pay_tran(self):
        """Process transfer with UPI verification"""
        self.text_for_check()
        
        ctk.CTkButton(self.frame_body,
                     text='Verify',
                     command=self.after_pay_tran).pack(pady=10)

    def after_pay_tran(self):
        """Complete transfer after verification"""
        self.hereamount = self.upi_validation()
        
        if self.hereamount == -1:
            CTkMessagebox(title="Error", 
                         message="Invalid UPI PIN",
                         icon="cancel")
            self.transfer()
            return

        self.money_tr = self.money_tran.get()
        self.acc_tr = self.acc_tran.get()

        # Validation
        if not self.money_tr.isdigit():
            CTkMessagebox(title="Error", 
                         message="Please enter a valid amount",
                         icon="cancel")
            return
            
        if not self.acc_tr.isdigit():
            CTkMessagebox(title="Error", 
                         message="Please enter a valid account number",
                         icon="cancel")
            return
            
        if self.acc_tr == self.vacc:
            CTkMessagebox(title="Error", 
                         message="Cannot transfer to your own account",
                         icon="cancel")
            return
            
    # Confirm transfer
        dialog = CTkMessagebox(
            title="Confirm Transfer",
            message=f"Send ${float(self.money_tr):,.2f} to account {self.acc_tr}?",
            icon="question",
            option_1="Cancel",
            option_2="Send"
        )
        
        if dialog.get() == "Send":
            self.return_tran = self.obj.pay(self.acc_tr, int(self.money_tr))
            
            if self.return_tran == 'lowbal':
                CTkMessagebox(title="Error", 
                             message="Insufficient funds",
                             icon="cancel")
            elif self.return_tran == -1:
                CTkMessagebox(title="Error", 
                             message="Invalid account number or transaction failed",
                             icon="cancel")
            else:
                CTkMessagebox(title="Success", 
                             message="Transfer completed successfully!",
                             icon="check")
                self.transfer()

    def search(self):
        """Modern search interface"""
        def pay_friend(value):
            """Payment dialog for search results"""
            self.frame_body.pack_forget()
            self.frame_body = ctk.CTkFrame(self.master)
            self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

            payment_frame = ctk.CTkFrame(self.frame_body)
            payment_frame.pack(expand=True, padx=20, pady=20)

            # Try to load friend's profile image
            try:
                friend_img = self.get_profile_image(value)
                if friend_img:
                    friend_img = friend_img.resize((80, 80))
                    self.friend_pay_image = ImageTk.PhotoImage(friend_img)
                    ctk.CTkLabel(payment_frame, image=self.friend_pay_image, text="").pack(pady=10)
            except Exception as e:
                print(f"Error loading friend's profile image in payment dialog: {e}")

            ctk.CTkLabel(payment_frame,
                        text=f"Send Money to {value}",
                        font=("Helvetica", 18, "bold")).pack(pady=10)

            amount_frame = ctk.CTkFrame(payment_frame)
            amount_frame.pack(pady=20)
            
            ctk.CTkLabel(amount_frame,
                        text="Amount: $",
                        font=("Helvetica", 14)).pack(side="left", padx=5)
                        
            self.money_tran_friend = ctk.CTkEntry(amount_frame,
                                                 width=200,
                                                 placeholder_text="Enter amount")
            self.money_tran_friend.pack(side="left", padx=5)

            button_frame = ctk.CTkFrame(payment_frame)
            button_frame.pack(pady=20)
            
            ctk.CTkButton(button_frame,
                         text='Send',
                         command=lambda: self.pay_tran_friend(value)).pack(side="left", padx=10)
                         
            ctk.CTkButton(button_frame,
                         text='Cancel',
                         command=self.search,
                         fg_color="transparent").pack(side="left", padx=10)

        def pay_friend_interm(value):
            """Show transaction history and payment options for search results"""
            self.transaction_history_friend(value)
            
            button_frame = ctk.CTkFrame(self.frame_body)
            button_frame.pack(pady=20)
            
            ctk.CTkButton(button_frame,
                         text='Send Money',
                         command=lambda: pay_friend(value)).pack(side="left", padx=10)
                         
            ctk.CTkButton(button_frame,
                         text='Back',
                         command=self.search,
                         fg_color="transparent").pack(side="left", padx=10)

        def search_list():
            """Process search and display results"""
            search_value = self.search_friend.get()
            try:
                result_name = self.obj.search_friend(search_value)
                if result_name and result_name != self.vname:
                    # Clear previous results
                    for widget in results_frame.winfo_children():
                        widget.destroy()
                        
                    # Show new result
                    result_button = ctk.CTkButton(
                        results_frame,
                        text=result_name,
                        command=lambda: pay_friend_interm(result_name),
                        height=40,
                        fg_color="transparent",
                        hover_color=("gray75", "gray25")
                    )
                    result_button.pack(fill="x", padx=5, pady=5)
                else:
                    CTkMessagebox(title="Not Found", 
                                message="No matching user found",
                                icon="info")
            except Exception as e:
                CTkMessagebox(title="Error", 
                            message="Search failed. Please try again.",
                            icon="cancel")

        # Main search interface
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Title
        ctk.CTkLabel(self.frame_body,
                    text="Search Users",
                    font=("Helvetica", 24, "bold")).pack(pady=20)

        # Search form
        form_frame = ctk.CTkFrame(self.frame_body)
        form_frame.pack(fill="x", padx=20, pady=20)

        # Search type selector
        search_type_var = ctk.StringVar(value="name")
        
        radio_frame = ctk.CTkFrame(form_frame)
        radio_frame.pack(fill="x", pady=10)
        
        ctk.CTkRadioButton(radio_frame,
                          text="Search by Name",
                          variable=search_type_var,
                          value="name").pack(side="left", padx=20)
                          
        ctk.CTkRadioButton(radio_frame,
                          text="Search by Phone",
                          variable=search_type_var,
                          value="phone").pack(side="left", padx=20)
                          
    # Search input
        search_frame = ctk.CTkFrame(form_frame)
        search_frame.pack(fill="x", pady=10)
        
        self.search_friend = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter name or phone number",
            width=300
        )
        self.search_friend.pack(side="left", padx=10)
        
        ctk.CTkButton(search_frame,
                     text="Search",
                     command=search_list).pack(side="left", padx=10)

        # Results area
        results_frame = ctk.CTkFrame(self.frame_body)
        results_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def profile(self):
        """Modern profile view interface"""
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Profile header with photo
        header_frame = ctk.CTkFrame(self.frame_body)
        header_frame.pack(fill="x", padx=20, pady=(20,10))

        # Load profile image
        try:
            profile_img = self.get_profile_image(self.vname)
            if profile_img:
                profile_img = profile_img.resize((100, 100))
                self.profile_image = ImageTk.PhotoImage(profile_img)
                ctk.CTkLabel(header_frame, image=self.profile_image, text="").pack(pady=10)
            else:
                # Only show "No Profile Image" if no image was loaded
                ctk.CTkLabel(header_frame, 
                            text="No Profile Image",
                            font=("Helvetica", 12)).pack(pady=10)
        except Exception as e:
            print(f"Error loading profile image: {e}")
            ctk.CTkLabel(header_frame, 
                        text="Error Loading Profile Image",
                        font=("Helvetica", 12)).pack(pady=10)

        # Personal Information Section
        ctk.CTkLabel(self.frame_body,
                    text="Personal Information",
                    font=("Helvetica", 18, "bold")).pack(pady=(10,20))

        details_frame = ctk.CTkFrame(self.frame_body)
        details_frame.pack(fill="x", padx=10)

        # Personal details
        personal_details = [
            ("Name:", self.vname),
            ("Email:", self.vemail),
            ("Date of Birth:", self.vdob),
            ("Mobile:", self.vphone),
            ("Address:", self.vaddress)
        ]

        for label, value in personal_details:
            row_frame = ctk.CTkFrame(details_frame)
            row_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row_frame,
                        text=label,
                        font=("Helvetica", 14, "bold"),
                        width=120,
                        anchor="e").pack(side="left", padx=10)
                        
            ctk.CTkLabel(row_frame,
                        text=value,
                        font=("Helvetica", 14),
                        anchor="w").pack(side="left", padx=10, fill="x", expand=True)

        # Banking Information Section
        ctk.CTkLabel(self.frame_body,
                    text="Banking Information",
                    font=("Helvetica", 18, "bold")).pack(pady=(20,10))

        bank_frame = ctk.CTkFrame(self.frame_body)
        bank_frame.pack(fill="x", padx=10)

        # Banking details
        banking_details = [
            ("Bank:", self.vbank),
            ("Account Number:", self.vacc)
        ]

        for label, value in banking_details:
            row_frame = ctk.CTkFrame(bank_frame)
            row_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row_frame,
                        text=label,
                        font=("Helvetica", 14, "bold"),
                        width=120,
                        anchor="e").pack(side="left", padx=10)
                        
            ctk.CTkLabel(row_frame,
                        text=value,
                        font=("Helvetica", 14),
                        anchor="w").pack(side="left", padx=10, fill="x", expand=True)

        # Action buttons
        button_frame = ctk.CTkFrame(self.frame_body)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame,
                     text='Edit Profile',
                     command=self.edit).pack(side="left", padx=10)
                     
        ctk.CTkButton(button_frame,
                     text='Change Password',
                     command=self.psd_change,
                     fg_color="transparent").pack(side="left", padx=10)
                     
    def edit(self):
        """Modern profile editing interface"""
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Title
        ctk.CTkLabel(self.frame_body,
                    text="Edit Profile",
                    font=("Helvetica", 24, "bold")).pack(pady=20)

        # Profile photo section
        photo_frame = ctk.CTkFrame(self.frame_body)
        photo_frame.pack(fill="x", padx=20, pady=10)

        # Load and display profile image
        profile_img = self.get_profile_image(self.vname)
        if profile_img:
            profile_img = profile_img.resize((100, 100))
            self.profile_image = ImageTk.PhotoImage(profile_img)
            ctk.CTkLabel(photo_frame,
                        image=self.profile_image,
                        text="").pack(pady=10)

        ctk.CTkButton(photo_frame,
                     text="Change Profile Picture",
                     command=self.edit_photo).pack(pady=10)

        # Edit form
        form_frame = ctk.CTkFrame(self.frame_body)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Email field
        email_frame = ctk.CTkFrame(form_frame)
        email_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(email_frame,
                    text='Email:',
                    font=("Helvetica", 14)).pack(side="left", padx=10)
                    
        self.edit_mail = ctk.CTkEntry(email_frame, width=300)
        self.edit_mail.pack(side="left", padx=10)
        self.edit_mail.insert(0, self.vemail)

        # Mobile field
        mobile_frame = ctk.CTkFrame(form_frame)
        mobile_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(mobile_frame,
                    text='Mobile:',
                    font=("Helvetica", 14)).pack(side="left", padx=10)
                    
        self.edit_mob = ctk.CTkEntry(mobile_frame, width=300)
        self.edit_mob.pack(side="left", padx=10)
        self.edit_mob.insert(0, self.vphone)

        # Address field
        address_frame = ctk.CTkFrame(form_frame)
        address_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(address_frame,
                    text='Address:',
                    font=("Helvetica", 14)).pack(side="left", padx=10)
                    
        self.edit_add = ctk.CTkEntry(address_frame, width=300)
        self.edit_add.pack(side="left", padx=10)
        self.edit_add.insert(0, self.vaddress)

        # Action buttons
        button_frame = ctk.CTkFrame(self.frame_body)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame,
                     text='Save Changes',
                     command=self.save_changes).pack(side="left", padx=10)
                     
        ctk.CTkButton(button_frame,
                     text='Cancel',
                     command=self.edit_cancel,
                     fg_color="transparent").pack(side="left", padx=10)
                     
        ctk.CTkButton(button_frame,
                     text='Change Password',
                     command=self.psd_change,
                     fg_color="transparent").pack(side="left", padx=10)

    def password_change(self):
        """Password change form"""
        # New password field
        new_pass_frame = ctk.CTkFrame(self.frame_body)
        new_pass_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(new_pass_frame,
                    text='New Password:',
                    font=("Helvetica", 14)).pack(side="left", padx=10)
                    
        self.edit_fp = ctk.CTkEntry(new_pass_frame,
                                   width=250,
                                   show="●",
                                   placeholder_text="Enter new password")
        self.edit_fp.pack(side="left", padx=10)

        # Confirm password field
        confirm_pass_frame = ctk.CTkFrame(self.frame_body)
        confirm_pass_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(confirm_pass_frame,
                    text='Confirm Password:',
                    font=("Helvetica", 14)).pack(side="left", padx=10)
                    
        self.edit_sp = ctk.CTkEntry(confirm_pass_frame,
                                   width=250,
                                   show="●",
                                   placeholder_text="Confirm new password")
        self.edit_sp.pack(side="left", padx=10)

    def psd_change(self):
        """Password change interface"""
        self.master.geometry('800x800')
        self.frame_body.pack_forget()
        
        self.frame_body = ctk.CTkFrame(self.master)
        self.frame_body.pack(pady=20, padx=20, fill="both", expand=True)

        # Title
        ctk.CTkLabel(self.frame_body,
                    text="Change Password",
                    font=("Helvetica", 24, "bold")).pack(pady=20)

        # Current password field
        current_pass_frame = ctk.CTkFrame(self.frame_body)
        current_pass_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(current_pass_frame,
                    text='Current Password:',
                    font=("Helvetica", 14)).pack(side="left", padx=10)
                    
        self.check_pass = ctk.CTkEntry(current_pass_frame,
                                      width=250,
                                      show="●",
                                      placeholder_text="Enter current password")
        self.check_pass.pack(side="left", padx=10)
    # Add password change fields
        self.password_change()

        # Action buttons
        button_frame = ctk.CTkFrame(self.frame_body)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame,
                     text='Change Password',
                     command=self.save_password).pack(side="left", padx=10)
                     
        ctk.CTkButton(button_frame,
                     text='Cancel',
                     command=self.edit,
                     fg_color="transparent").pack(side="left", padx=10)

    def validate_password(self):
        """Validate password change with hashing"""
        hashed_current = hash_password(self.check_pass.get())
        if hashed_current == self.vpass:
            if self.edit_sp.get() == self.edit_fp.get():
                if len(self.edit_fp.get()) < 6:
                    CTkMessagebox(title="Error", 
                                message="Password must be at least 6 characters long",
                                icon="cancel")
                    return False
                    
                hashed_new = hash_password(self.edit_fp.get())
                self.obj.change_password(self.vname, hashed_new)
                CTkMessagebox(title="Success", 
                            message="Password changed successfully!",
                            icon="check")
                self.home()
                return True
            else:
                CTkMessagebox(title="Error", 
                            message="New passwords don't match",
                            icon="cancel")
        else:
            CTkMessagebox(title="Error", 
                        message="Current password is incorrect",
                        icon="cancel")
        return False

    def save_password(self):
        """Save new password"""
        self.validate_password()
        if not self.validate_password():
            self.psd_change()

    def save_changes(self):
        """Save profile changes with confirmation"""
        dialog = CTkMessagebox(
            title="Save Changes",
            message="Are you sure you want to save these changes?",
            icon="question",
            option_1="Cancel",
            option_2="Save"
        )
        
        if dialog.get() == "Save":
            # Validate email
            email_pattern = re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|edu|net)', self.edit_mail.get())
            if not email_pattern:
                CTkMessagebox(title="Error", 
                            message="Please enter a valid email address",
                            icon="cancel")
                return

            # Validate phone
            if not self.edit_mob.get().isdigit() or len(self.edit_mob.get()) != 10:
                CTkMessagebox(title="Error", 
                            message="Please enter a valid 10-digit phone number",
                            icon="cancel")
                return

            # Update profile
            self.vemail = self.edit_mail.get()
            self.vphone = self.edit_mob.get()
            self.vaddress = self.edit_add.get()
            
            self.obj.update_record(self.uid, self.vemail, self.vphone, self.vaddress)
            
            CTkMessagebox(title="Success", 
                        message="Profile updated successfully!",
                        icon="check")
            self.profile()

    def edit_cancel2(self):
        """Cancel transaction changes"""
        dialog = CTkMessagebox(
            title="Cancel Changes",
            message="Are you sure you want to cancel?",
            icon="warning",
            option_1="No",
            option_2="Yes"
        )
        
        if dialog.get() == "Yes":
            if hasattr(self, 'acc_tran'):
                self.acc_tran.delete(0, 'end')
            if hasattr(self, 'money_tran'):
                self.money_tran.delete(0, 'end')

    def edit_cancel_create(self):
        """Cancel account creation"""
        dialog = CTkMessagebox(
            title="Cancel Creation",
            message="Are you sure you want to cancel? All entered data will be lost.",
            icon="warning",
            option_1="No",
            option_2="Yes"
        )
        
        if dialog.get() == "Yes":
            for field in ['name', 'email', 'dob', 'phone', 'address', 
                         'pswd', 'repswd', 'upi', 'reupi']:
                if hasattr(self, field):
                    getattr(self, field).delete(0, 'end')

    def edit_cancel(self):
        """Cancel profile edits"""
        dialog = CTkMessagebox(
            title="Cancel Changes",
            message="Are you sure you want to discard your changes?",
            icon="warning",
            option_1="No",
            option_2="Yes"
        )
        
        if dialog.get() == "Yes":
            if hasattr(self, 'edit_mail') and self.edit_mail.get() != self.vemail:
                self.edit_mail.delete(0, 'end')
                self.edit_mail.insert(0, self.vemail)
                
            if hasattr(self, 'edit_mob') and self.edit_mob.get() != self.vphone:
                self.edit_mob.delete(0, 'end')
                self.edit_mob.insert(0, self.vphone)
                
            if hasattr(self, 'edit_add') and self.edit_add.get() != self.vaddress:
                self.edit_add.delete(0, 'end')
                self.edit_add.insert(0, self.vaddress)
                
    def get_profile_image(self, username):
        """
        Retrieves the profile image for a given username from the profile_images directory.
        Returns the image data if found, None otherwise.
        """
        import os
        from PIL import Image, ImageTk
        
        # Construct the path to the profile image
        image_path = os.path.join("profile_images", f"{username}.jpg")
        
        # Check if the profile_images directory exists, if not create it
        if not os.path.exists("profile_images"):
            os.makedirs("profile_images")
        
        # Try to open and return the image
        try:
            img = Image.open(image_path)
            # Create a copy in memory to avoid file handle issues
            img_copy = img.copy()
            img.close()
            return img_copy
        except Exception as e:
            print(f"Error loading profile image for {username}: {e}")
            return None
    # Main execution
if __name__ == "__main__":
    # Create the main window
    root = ctk.CTk()
    
    # Set window title
    root.title("SecureBank")
    
    # Center the window on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate position
    x = (screen_width/2) - (800/2)
    y = (screen_height/2) - (600/2)
    
    # Set the window's position
    root.geometry(f'800x800+{int(x)}+{int(y)}')
    
    # Create application instance
    app = Front(root)
    
    # Start the application
    root.mainloop()