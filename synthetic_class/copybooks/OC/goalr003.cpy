******************************************************************
*  COPYBOOK  : GOALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : AL
******************************************************************
 01  RT-OAL-RATING.

          03 RT-OAL-TERRITORY-CODE            PIC X(3).
          03 RT-OAL-CLASS-CODE                PIC X(4).
          03 RT-OAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OAL-RATED-PREMIUM             PIC 9(9)V9(2).
