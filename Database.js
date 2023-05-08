// Import the Firebase SDK
import firebase from 'firebase/app';
import 'firebase/auth';
import 'firebase/database';

// Initialize Firebase
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  databaseURL: "YOUR_DATABASE_URL",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

firebase.initializeApp(firebaseConfig);

// Access the authentication service
const auth = firebase.auth();

// Access the realtime database service
const database = firebase.database();

// Authenticate a user with email and password
auth.signInWithEmailAndPassword(email, password)
  .then((userCredential) => {
    // User signed in successfully
    const user = userCredential.user;
    console.log('User signed in: ', user);
  })
  .catch((error) => {
    // An error occurred while signing in
    const errorCode = error.code;
    const errorMessage = error.message;
    console.error('Error signing in: ', errorCode, errorMessage);
  });

// Read data from the database
database.ref('path/to/data').once('value')
  .then((snapshot) => {
    // Data was read successfully
    const data = snapshot.val();
    console.log('Data: ', data);
  })
  .catch((error) => {
    // An error occurred while reading data
    const errorCode = error.code;
    const errorMessage = error.message;
    console.error('Error reading data: ', errorCode, errorMessage);
  });

// Write data to the database
database.ref('path/to/data').set({
  // data to be written
})
  .then(() => {
    // Data was written successfully
    console.log('Data was written successfully');
  })
  .catch((error) => {
    // An error occurred while writing data
    const errorCode = error.code;
    const errorMessage = error.message;
    console.error('Error writing data: ', errorCode, errorMessage);
  });
