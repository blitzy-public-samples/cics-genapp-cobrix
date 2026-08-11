******************************************************************
*  COPYBOOK  : GONCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : NC
******************************************************************
 01  RT-ONC-RATING.

          03 RT-ONC-TERRITORY-CODE            PIC X(3).
          03 RT-ONC-CLASS-CODE                PIC X(4).
          03 RT-ONC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ONC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ONC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ONC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ONC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ONC-RATED-PREMIUM             PIC 9(9)V9(2).
