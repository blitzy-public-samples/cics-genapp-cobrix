******************************************************************
*  COPYBOOK  : GOAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : AZ
******************************************************************
 01  RT-OAZ-RATING.

          03 RT-OAZ-TERRITORY-CODE            PIC X(3).
          03 RT-OAZ-CLASS-CODE                PIC X(4).
          03 RT-OAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OAZ-RATED-PREMIUM             PIC 9(9)V9(2).
