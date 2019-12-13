void updateMotorParams(AccelStepper50pctDuty & motor) {           // Passes motor by reference so that it can be used for sub and targets
    float startSpeed = motor.speed();

    if (inCommandType == 'u') {
        switch (inCommandParam) {
            case 'a':                       // Set acceleration if parameter to update is 'a'
                motor.setAcceleration(inCommandValFloat);
                commandReady = false;
                break;
            case 'm':                       // Set max speed if parameter to update is 'm'
                motor.setMaxSpeed(inCommandValFloat);
                commandReady = false;
                break;
            case 'v':                       // Set motor speed if parameter to update is 'v'elocity
                motor.setSpeed(inCommandValFloat);
                commandReady = false;
                break;
            case 'g':                       // Set new goal position and reset speed as moveTo calculates new speeds
                motor.moveTo(inCommandValInt);
                //motor.setSpeed(startSpeed);
                commandReady = false;
                break;
            case 'd':                       // Used for + or - manual stepping
                if (inCommandValInt == 1) { // Move cw one step
                    motor.move(1);
                    motor.setSpeed(startSpeed);
                }
                else if (inCommandValInt == 0) {    // Move ccw one step
                    motor.move(-1);
                    motor.setSpeed(startSpeed);
                }
                break;                      // NOTE: Not setting commandReady to false so this repeats until
                                            // told otherwise by serial
            case 'r':
                if (inCommandAxis != 't') {
                  commandReady = false;     // Only raster if the target is the selected command axis
                  break;                    // Break early
                }
                
                // If we are currently centering the target, maintain the center value, 
                // otherwise set raster center to the current position
                if (centering == false) {
                  rasterCenter = motor.targetPosition();
                }
                
                // Set the raster steps based on input
                if (inCommandValInt == 0){
                  rasterSteps = 0;
                  rasterSide = 0;   // Flag main loop to move back to target center
                  rasterOn = false;
                }
                else if (inCommandValInt == 1) {
                  rasterSteps = 31;
                  rasterOn = true;
                }
                else if (inCommandValInt == 2) {
                  rasterSteps = 63;
                  rasterOn = true;
                }
                commandReady = false;
                break;
        }
    }
    else if (inCommandType == 'q') {
      switch(inCommandParam) {
        case 'p':
          Serial.println(motor.currentPosition());
          break;
        case 'm':
          Serial.println(motor.maxSpeed());
          break;
        case 'v':
          Serial.println(motor.speed());
          break;
        case 'g':
          Serial.println(motor.targetPosition());
          break;
        case 'd':
          Serial.println(motor.distanceToGo());
          break;
        case 'r':
          Serial.println(motor.isRunning());
          break;
        }
        commandReady = false;
    }
    else if (inCommandType == 'h') {
        // May need to consider cranking acceleration here to stop faster
        motor.stop();                   // May need to switch to disableOutputs to up reaction speed
        commandReady = false;              // Finishes this command and prevents re updating
    }
    if (commandReady == false) {                  // If we set command ready to false, clear command variable values
            clearAxisModVars();
        }
}