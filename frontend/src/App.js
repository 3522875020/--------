import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import MainMenu from './components/MainMenu';
import Quiz from './components/Quiz';
import Result from './components/Result';

function App() {
  return (
    <Router>
      <div className="App">
        <Switch>
          <Route exact path="/" component={MainMenu} />
          <Route path="/quiz" component={Quiz} />
          <Route path="/result" component={Result} />
        </Switch>
      </div>
    </Router>
  );
}

export default App; 