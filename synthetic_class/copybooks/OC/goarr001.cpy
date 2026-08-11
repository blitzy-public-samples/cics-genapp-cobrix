******************************************************************
*  COPYBOOK  : GOARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : AR
******************************************************************
 01  RT-OAR-RATING.

          03 RT-OAR-TERRITORY-CODE            PIC X(3).
          03 RT-OAR-CLASS-CODE                PIC X(4).
          03 RT-OAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OAR-RATED-PREMIUM             PIC 9(9)V9(2).
