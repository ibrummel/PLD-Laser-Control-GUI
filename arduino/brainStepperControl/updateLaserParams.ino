void updateLaserParams(AccelStepper & laser) {           // Passes laser by reference so that it can be used for sub and targets
    //float startSpeed = laser.speed();

    if (inCommandType == 'u') {
        switch (inCommandParam) {
            case 'r':
                if (inCommandValLong > 20){
                  laser.setMaxSpeed(20);
                }
                else if (inCommandValLong < 20 && inCommandValLong >= 0) {
                  laser.setMaxSpeed(inCommandValLong);
                }
                else if (inCommandValLong < 0) {
                  laser.setMaxSpeed(-1 * inCommandValLong);
                }
                commandReady = false;
                break;
            case 'g':                       // Set the goal to be whatever number of pulses are sent over serial
                laserRunIndef = false;
                laser.setCurrentPosition(0);  // Reset the number of laser pulses
                laser.move(inCommandValLong);
                commandReady = false;
                break;
            case 'd':                       // Used to run without a set number of pulses
                laserRunIndef = true;
                //laser.setSpeed(startSpeed);
                break;                      // NOTE: Not setting commandReady to false so this repeats until
                                            // told otherwise by serial
        }
    }
    else if (inCommandType == 'q') {
      switch(inCommandParam) {
        case 'p':
          Serial.println(laser.currentPosition());
          break;
        case 'm':
          Serial.println(laser.maxSpeed());
          break;
        case 'v':
          Serial.println(laser.speed());
          break;
        case 'g':
          Serial.println(laser.targetPosition());
          break;
        case 'd':
          Serial.println(laser.distanceToGo());
          break;
        case 'r':
          Serial.println(laser.isRunning());
          break;
        }
        commandReady = false;
    }
    else if (inCommandType == 'h') {
        // May need to consider cranking acceleration here to stop faster
        laser.stop();                   // May need to switch to disableOutputs to up reaction speed
        laserRunIndef = false;
        commandReady = false;              // Finishes this command and prevents re updating
    }
    if (commandReady == false) {                  // If we set command ready to false, clear command variable values
        clearAxisModVars();
    }
}
