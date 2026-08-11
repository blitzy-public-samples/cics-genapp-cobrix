******************************************************************
*  COPYBOOK  : GOAKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : AK
******************************************************************
 01  RT-OAK-RATING.

          03 RT-OAK-TERRITORY-CODE            PIC X(3).
          03 RT-OAK-CLASS-CODE                PIC X(4).
          03 RT-OAK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OAK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OAK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OAK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OAK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OAK-RATED-PREMIUM             PIC 9(9)V9(2).
