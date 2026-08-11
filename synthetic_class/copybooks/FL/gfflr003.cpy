******************************************************************
*  COPYBOOK  : GFFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : FL
******************************************************************
 01  RT-FFL-RATING.

          03 RT-FFL-TERRITORY-CODE            PIC X(3).
          03 RT-FFL-CLASS-CODE                PIC X(4).
          03 RT-FFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FFL-RATED-PREMIUM             PIC 9(9)V9(2).
