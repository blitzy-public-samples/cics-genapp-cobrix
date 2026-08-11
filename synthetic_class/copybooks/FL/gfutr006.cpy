******************************************************************
*  COPYBOOK  : GFUTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : UT
******************************************************************
 01  RT-FUT-RATING.

          03 RT-FUT-TERRITORY-CODE            PIC X(3).
          03 RT-FUT-CLASS-CODE                PIC X(4).
          03 RT-FUT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FUT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FUT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FUT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FUT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FUT-RATED-PREMIUM             PIC 9(9)V9(2).
